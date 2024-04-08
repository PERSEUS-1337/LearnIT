import os
import json
import sys
import paths
import params
from dotenv import load_dotenv
from models import Document, Extracted, TextChunk
from pprint import pprint

from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader

from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.schema import StrOutputParser


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Create output directories if they don't exist
os.makedirs(paths.OUTPUT_PATH, exist_ok=True)

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")



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
            chunk_size=750,
            chunk_overlap=250
        )
        text_list = text_splitter.split_text(json_data['content'])

        text_chunks = [TextChunk(chunk) for chunk in text_list]
        
        prev_chunk = ""
        for i, chunk in enumerate(text_chunks):
            chunk.prev = prev_chunk
            prev_chunk = chunk.curr
            print(f"{i}. {chunk}\n")

        # return text_chunks


def llm_process(curr_chunk, prev_chunk, chosen_model):
    """Process the extracted prev and curr chunks into a single condensed chunk

    Args:
        curr_chunk (str): contains chunk to be condensed
        prev_chunk (str): contains chunk before curr_chunk to aid in context
        chosen_model (str): choose between "3.5-turbo" or "4-turbo-preview"

    Returns:
        condensed_chunk (str): condensed text to be returned
    """

    prompt_template = """
        Follow the steps to provide a condensed text chunk:
        
        Step 1: Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words
        
        {curr_chunk}

        Step 2: After processing the curr_chunk, use the prev_chunk to adjust your output accordingly, and to ensure there is proper information flow for user reading
        
        {prev_chunk}

        Step 3: Output the condensed chunk itself
    """

    # Create a PromptTemplate instance
    prompt = PromptTemplate.from_template(template=prompt_template)

    prompt_formatted_str = prompt.format(curr_chunk=curr_chunk, prev_chunk=prev_chunk)

    # Instantiate the OpenAI instance
    llm = OpenAI(model=chosen_model)
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # Run the LLM chain with your input chunks
    response = llm_chain.run({"curr_chunk": curr_chunk, "prev_chunk": prev_chunk})

    # Process the response
    output_parser = StrOutputParser()
    parsed_response = output_parser.parse(response)

    # Print the parsed response
    print(parsed_response)


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
