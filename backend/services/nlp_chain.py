import os
import os
import json
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    PyPDFium2Loader,
    TextLoader,
    PyMuPDFLoader,
)

from utils.consts import UPLOAD_PATH
from models.document import TSCC
from utils.config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, LLM_TEMP, LLMS, PROMPT_2_1, PROMPT_2_2, PROMPT_MAIN

def tokenize(document):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )
    text_chunks = text_splitter.split_documents(document)
    
    return text_chunks
    
    
def process_document(filename, loader_choice="PyMuPDFLoader") -> TSCC:
    # Append the file string to "./datasets/downloaded_documents"
    file_path = os.path.join(UPLOAD_PATH, filename)
    
    # Initialize PyPDFLoader with the file path
    if loader_choice == "PyPDFLoader":
        loader = PyPDFLoader(file_path)
    elif loader_choice == "PyPDFium2Loader":
        loader = PyPDFium2Loader(file_path)
    elif loader_choice == "PyMuPDFLoader":
        loader = PyMuPDFLoader(file_path)
    elif loader_choice == "TextLoader":
        loader = TextLoader(file_path)

    document = loader.load()

    # Split texts into chunks
    text_chunks = tokenize(document)

    # print(json.dumps(str(text_chunks)))

    # # print(len(text_chunks))
    # prev_chunk = ""
    # for i, chunk in enumerate(text_chunks):
    #     chunk.metadata["index"] = i
    #     chunk.metadata["prev_chunk"] = prev_chunk
    #     # print(f"{i}: {chunk.page_content}\n")
    #     prev_chunk = chunk.page_content
    #     # chunk.metadata["global"] = document

    return text_chunks      