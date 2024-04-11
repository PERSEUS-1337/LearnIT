import os
import json
import sys
import paths
import params

from dotenv import load_dotenv
from models import Extracted

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

from utils import log_error, write_to_file


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Create output directories if they don't exist
os.makedirs(paths.OUTPUT_PATH, exist_ok=True)
os.makedirs(paths.OUTPUT_PATH_1, exist_ok=True)
os.makedirs(paths.OUTPUT_PATH_2, exist_ok=True)
os.makedirs(paths.OUTPUT_PATH_3, exist_ok=True)

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


def add_context_to_chunk(text_chunks: list):
    """Adds the previous chunk to the current chunk as part of its object properites

    Args:
        - text_chunks (list): _description_
    """
    prev_chunk = ""
    for i, chunk in enumerate(text_chunks):
        chunk.prev = prev_chunk
        prev_chunk = chunk.curr
        print(f"{i}. {chunk}\n")


def tscc_process(
    json_data,
    size=params.DEFAULT_CHUNK_SIZE,
    overlap=params.DEFAULT_CHUNK_OVERLAP,
    chosen_model=params.LLMS["dev"],
):
    """_summary_

    Args:
        - json_data (json): contains the json formatted text extracted from the json files, that is to be proccsed by TSCC

    Returns:
        - str: Combined summaries generated by the TSCC from the json_dara
    """
    print(f"> {json_data['title']} - tscc_process():\n", end="", flush=True)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap
    )
    text_list = text_splitter.split_text(json_data["content"])

    processed_chunks = []
    prev_chunk = ""

    for curr_chunk in text_list:
        result = llm_process(curr_chunk, prev_chunk, chosen_model)
        prev_chunk = result
        processed_chunks.append(result)

        # Update progress bar
        progress = len(processed_chunks) / len(text_list) * 100
        print(
            f"\t[{'#' * int(progress/10)}{'-' * (10 - int(progress/10))}] {int(progress)}%",
            end="\r",
            flush=True,
        )

    combined_str = " ".join(processed_chunks)
    print("> DONE!\t")

    return combined_str


def llm_process(curr_chunk, prev_chunk, chosen_model, tscc_type=0) -> str:
    """_summary_

    Args:
        curr_chunk (str): The text that is to be condensed by TSCC
        prev_chunk (str): The text that provides context to aid the TSCC
        chosen_model (str, optional): Can choose between 3.5-turbo or 4-turbo-preview
        tscc_type (int, optional): For testing purposes, choosing between the type of TSCC for varied outputs. Defaults to 0.

    Returns:
        str: The chunk of text that has been condensed by the TSCC
    """

    turbo_llm = ChatOpenAI(temperature=params.LLM_TEMP, model_name=chosen_model)

    if tscc_type == 0:
        prompt = PromptTemplate.from_template(template=params.PROMPT_MAIN)
        llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
        response = llm_chain.invoke(
            {"curr_chunk": curr_chunk, "prev_chunk": prev_chunk}
        )
        # print(llm_chain.invoke({"curr_chunk": curr_chunk, "prev_chunk": prev_chunk}))
        # return llm_chain.run({"curr_chunk": curr_chunk, "prev_chunk": prev_chunk})
        return response["text"]

    if tscc_type == 1:
        prompt = PromptTemplate.from_template(template=params.PROMPT_2_1)

        llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
        return llm_chain.run({"curr_chunk": curr_chunk})

    if tscc_type == 2:
        prompt_1 = PromptTemplate.from_template(template=params.PROMPT_2_1)

        llm_chain = LLMChain(prompt=prompt_1, llm=turbo_llm)
        response = llm_chain.run({"curr_chunk": curr_chunk})

        prompt_2 = PromptTemplate.from_template(template=params.PROMPT_2_2)
        llm_chain = LLMChain(prompt=prompt_2, llm=turbo_llm)

        return llm_chain.run({"curr_chunk": response, "prev_chunk": prev_chunk})


def summarize_document():
    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")
    file_name = "SCI_Tu1NiBXxf0.json"

    file_path = os.path.join("./extracted_data/test", file_name)
    print(f"> Processing {file_name}")

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            json_data = json.load(file)
            # tscc_process(json_data)
            processed_content = tscc_process(json_data)
            extracted = Extracted(json_data["title"], processed_content)
            write_to_file(extracted, file_name, paths.OUTPUT_PATH)

        except Exception as e:
            # Log the error to the error log file
            log_error(file_name, str(e), error_log_file)

    print("> Processing complete.")


def test_types():
    # Define the folders to save the processed data
    output_folders = [os.path.join(paths.OUTPUT_PATH, str(i)) for i in range(3)]

    # Iterate over each output folder
    for folder_index, output_folder in enumerate(output_folders):
        files_to_process = os.listdir("./extracted_data/test")
        for file_name in files_to_process:
            file_path = os.path.join("./extracted_data/test", file_name)
            print(f"> Processing: {file_name}")

            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=params.CHUNK_SIZE, chunk_overlap=params.CHUNK_OVERLAP
                )
                text_list = text_splitter.split_text(json_data["content"])

                processed_chunks = []
                prev_chunk = ""

                for i, curr_chunk in enumerate(text_list):
                    result = llm_process(
                        curr_chunk, prev_chunk, "gpt-3.5-turbo", folder_index
                    )
                    prev_chunk = result
                    processed_chunks.append(result)

                extracted = Extracted(json_data["title"], processed_chunks)

                # # Save the processed data to the current output folder
                write_to_file(extracted, file_name, output_folder)

            print(f"> Saved processed data to folder {folder_index}")

    print("> Processing complete.")


def main():
    """Main Menu for testing purposes"""
    while True:
        print("\nText Segmentation and Contextual Condensing\n===========")
        print("[1] Test 1 document on main prompt choice")
        print("[2] Test 1 document on 3 prompt choices")
        choice = input(">Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            # file = input(">Enter filename: ")
            summarize_document()
        elif choice == "2":
            test_types()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
