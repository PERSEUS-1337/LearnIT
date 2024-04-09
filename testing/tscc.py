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

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


def write_to_file(chunk_data, file_name):
    """_summary_

    Args:
        chunk_data (_type_): _description_
    """

    output_path = os.path.join(paths.OUTPUT_PATH, file_name)
    # if chunk_data:  # Check if sum_data is not empty
    with open(output_path, "w") as file:
        json.dump(chunk_data, file, cls=ExtractedEncoder, indent=4)


def add_context_to_chunk(text_chunks: list):
    prev_chunk = ""
    for i, chunk in enumerate(text_chunks):
        chunk.prev = prev_chunk
        prev_chunk = chunk.curr
        print(f"{i}. {chunk}\n")
        

def process_document():
    # files_to_process = os.listdir(paths.REFERENCES_PATH)
    file_name = "GOVR_93-792.json"
    # for i, file_name in enumerate(files_to_process):
    #     if i >= 1:
    #         break 
    file_path = os.path.join(paths.REFERENCES_PATH, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=250
        )
        text_list = text_splitter.split_text(json_data['content'])

        # text_chunks = [TextChunk(chunk) for chunk in text_list]
        # add_context_to_chunk(text_chunks)
        
        processed_chunks = []
        prev_chunk = ""
        for i, curr_chunk in enumerate(text_list):
            result = llm_process(curr_chunk, prev_chunk, "gpt-3.5-turbo")
            print(f"{result}\n\n")
            prev_chunk = result
            processed_chunks.append(result)
        combined_str = " ".join(processed_chunks)
        extracted = Extracted(json_data['title'], combined_str)
        
        # print(processed_chunks)
        write_to_file(extracted, file_name)
        # print("ok")



def llm_process(curr_chunk, prev_chunk, chosen_model):
    """Process the extracted prev and curr chunks into a single condensed chunk

    Args:
        curr_chunk (str): contains chunk to be condensed
        prev_chunk (str): contains chunk before curr_chunk to aid in context
        chosen_model (str): choose between "3.5-turbo" or "4-turbo-preview"

    Returns:
        condensed_chunk (str): condensed text to be returned
    """

    turbo_llm = ChatOpenAI(temperature=0.7, model_name=chosen_model)

    # Create a PromptTemplate instance
    prompt = PromptTemplate.from_template(template=params.PROMPT_TEMPLATE)

    llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
    return llm_chain.run(
        {
            "curr_chunk": curr_chunk,
            "prev_chunk": prev_chunk
        }
    )


def main():
    """Main Menu for testing purposes"""
    while True:
        print("\nProcess Documents for TSCC Outputs\n===========")
        print("1. Process 1 test document")
        choice = input("Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            process_document()
        elif choice == "2":
            process_json()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
