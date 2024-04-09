import os
import json
import sys
import paths
import params

from dotenv import load_dotenv
from models import Document, Extracted, ExtractedEncoder, TextChunk
from pprint import pprint

from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain.chains import LLMChain
from langchain.schema import StrOutputParser


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Create output directories if they don't exist
os.makedirs(paths.OUTPUT_PATH, exist_ok=True)
os.makedirs(paths.OUTPUT_PATH_1, exist_ok=True)
os.makedirs(paths.OUTPUT_PATH_2, exist_ok=True)
os.makedirs(paths.OUTPUT_PATH_3, exist_ok=True)

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


def write_to_file(chunk_data, file_name, file_path=paths.OUTPUT_PATH):
    """_summary_

    Args:
        chunk_data (_type_): _description_
    """

    output_path = os.path.join(file_path, file_name)
    with open(output_path, "w") as file:
        json.dump(chunk_data, file, cls=ExtractedEncoder, indent=4)
    print("File saved")


def add_context_to_chunk(text_chunks: list):
    prev_chunk = ""
    for i, chunk in enumerate(text_chunks):
        chunk.prev = prev_chunk
        prev_chunk = chunk.curr
        print(f"{i}. {chunk}\n")
        

def process_document():
    # files_to_process = os.listdir(paths.REFERENCES_PATH)
    file_name = "SCI_Tu1NiBXxf0.json"
    file_path = os.path.join(paths.REFERENCES_PATH, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=params.CHUNK_SIZE,
            chunk_overlap=params.CHUNK_OVERLAP
        )
        text_list = text_splitter.split_text(json_data['content'])

        # text_chunks = [TextChunk(chunk) for chunk in text_list]
        # add_context_to_chunk(text_chunks)
        
        processed_chunks = []
        prev_chunk = ""
        
        for i, curr_chunk in enumerate(text_list):
            print(f"{i}. {prev_chunk}")
            result = llm_process(curr_chunk, prev_chunk, "gpt-3.5-turbo")
            prev_chunk = result
            processed_chunks.append(result)
            
            # print(f"{i}. Result: \n{result}\n")
        # combined_str = " ".join(processed_chunks)
        extracted = Extracted(json_data['title'], processed_chunks)
        
        # print(processed_chunks)
        write_to_file(extracted, file_name)


def test_types():
    # Define the folders to save the processed data
    output_folders = [os.path.join(paths.OUTPUT_PATH, str(i)) for i in range(3)]

    # Iterate over each output folder
    for folder_index, output_folder in enumerate(output_folders):
        files_to_process = os.listdir('./extracted_data/test')
        for file_name in files_to_process:
            file_path = os.path.join('./extracted_data/test', file_name)
            print(f"Processing: {file_name}")

            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=params.CHUNK_SIZE,
                    chunk_overlap=params.CHUNK_OVERLAP
                )
                text_list = text_splitter.split_text(json_data['content'])
                
                processed_chunks = []
                prev_chunk = ""
                
                for i, curr_chunk in enumerate(text_list):
                    # print(f'{i}. \n{curr_chunk}\n')
                    result = llm_process(curr_chunk, prev_chunk, "gpt-3.5-turbo", folder_index)
                    prev_chunk = result
                    print(f'Result:\n{result}\n')
                    processed_chunks.append(result)

                extracted = Extracted(json_data['title'], processed_chunks)
                # combined_str = " ".join(processed_chunks)
                # extracted = Extracted(json_data['title'], combined_str)

                # # Save the processed data to the current output folder
                write_to_file(extracted, file_name, output_folder)

            print(f"Saved processed data to folder {folder_index}")

    print("Processing complete.")



def llm_process(curr_chunk, prev_chunk, chosen_model, tscc_type=0):
    """Process the extracted prev and curr chunks into a single condensed chunk

    Args:
        curr_chunk (str): contains chunk to be condensed
        prev_chunk (str): contains chunk before curr_chunk to aid in context
        chosen_model (str): choose between "3.5-turbo" or "4-turbo-preview"

    Returns:
        condensed_chunk (str): condensed text to be returned
    """
    try:
        turbo_llm = ChatOpenAI(temperature=0.7, model_name=chosen_model)
        
        if tscc_type == 0:
            prompt = PromptTemplate.from_template(template=params.PROMPT_MAIN)
            llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)

            return llm_chain.run(
                {
                    "curr_chunk": curr_chunk,
                    "prev_chunk": prev_chunk
                }
            )

        if tscc_type == 1:
            prompt = PromptTemplate.from_template(template=params.PROMPT_2_1)

            llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
            return llm_chain.run(
                {
                    "curr_chunk": curr_chunk
                }
            )
        
        if tscc_type == 2:
            prompt_1 = PromptTemplate.from_template(template=params.PROMPT_2_1)

            llm_chain = LLMChain(prompt=prompt_1, llm=turbo_llm)
            response = llm_chain.run(
                {
                    "curr_chunk": curr_chunk
                }
            )
        
            prompt_2 = PromptTemplate.from_template(template=params.PROMPT_2_2)
            llm_chain = LLMChain(prompt=prompt_2, llm=turbo_llm)
            
            return llm_chain.run(
                {
                    "curr_chunk": response,
                    "prev_chunk": prev_chunk
                }
            )
    except Exception as e:
        print(f"Error in llm_process: {e}")
        return ""



def main():
    """Main Menu for testing purposes"""
    while True:
        print("\nProcess Documents for TSCC Outputs\n===========")
        choice = input("Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            process_document()
        elif choice == "2":
            test_types()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
