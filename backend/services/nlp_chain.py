from datetime import datetime
import os
import re
from dotenv import dotenv_values
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    PyPDFium2Loader,
    TextLoader,
    PyMuPDFLoader,
)

from models.document import TSCC
from utils.config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    LLM_TEMP,
    LLMS,
    PROMPT_2_1,
    PROMPT_2_2,
    PROMPT_MAIN,
)

config = dotenv_values(".env")


def extract_page_content(chunk: str) -> str:
    """Extract page content from a chunk string."""
    match = re.search(r"page_content='(.*?)' metadata=", chunk, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def tokenizer(document):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )
    text_chunks = text_splitter.split_documents(document)

    # page_contents = extract_page_content(documents)

    return text_chunks


def extract_tokens(filename, loader_choice="PyPDFium2Loader") -> TSCC:
    file_path = os.path.join(config["UPLOAD_PATH"], filename)

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
    text_chunks = tokenizer(document)

    print(f"DEV:\t{len(text_chunks)} Chunk Count")

    # Extract page_content from each chunk
    text_chunks = [extract_page_content(str(chunk)) for chunk in text_chunks]

    # Construct the TSCC object
    tscc = TSCC(
        uid=filename,  # Assuming filename is used as the UID
        processed=datetime.now(),
        chunks=text_chunks,
        model_used="model-v1",  # Replace with actual model name if applicable
        doc_loader_used=loader_choice,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        token_count=sum(len(chunk.split()) for chunk in text_chunks),
        chunks_generated=len(text_chunks),
    )

    return tscc
