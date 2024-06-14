from datetime import datetime
import os
import re
import time
from typing import Dict, List
from dotenv import dotenv_values, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
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

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def extract_page_content(chunk: str) -> str:
    """Extract page content from a chunk string."""
    match = re.search(r"page_content='(.*?)' metadata=", chunk, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def tokenizer(document) -> List[Dict[str, str]]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )
    text_chunks = text_splitter.split_documents(document)

    # Extract page_content from each chunk
    text_chunks = [extract_page_content(str(chunk)) for chunk in text_chunks]

    # Create a list of dicts with 'prev' and 'curr'
    chunk_dicts = []
    for i in range(len(text_chunks)):
        chunk_dicts.append(
            {"prev": text_chunks[i - 1] if i > 0 else "", "curr": text_chunks[i]}
        )

    return chunk_dicts


def llm_process(curr_chunk, prev_chunk, chosen_model=LLMS["dev"]) -> str:
    """_summary_

    Args:
        curr_chunk (str): The text that is to be condensed by TSCC
        prev_chunk (str): The text that provides context to aid the TSCC
        chosen_model (str, optional): Can choose between 3.5-turbo or 4-turbo-preview

    Returns:
        str: The chunk of text that has been condensed by the TSCC
    """

    turbo_llm = ChatOpenAI(temperature=LLM_TEMP, model_name=chosen_model)

    prompt = PromptTemplate.from_template(template=PROMPT_MAIN)
    llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
    response = llm_chain.invoke(
        {"curr_chunk": curr_chunk, "prev_chunk": prev_chunk}
    )
    return response["text"]


def summarize_tokens(filename, loader_choice="PyPDFium2Loader") -> TSCC:
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
        
    start_time = time.time()  # Record start time
    print(f"> [PROCESS]\t{filename} - TSCC():\n", end="", flush=True)


    document = loader.load()

    # Split texts into chunks
    chunk_dicts = tokenizer(document)

    processed_chunks = []
    for chunk in chunk_dicts:
        # print(f"Curr Chunk: {chunk['curr']}\nPrev Chunk: {chunk['prev']}")
        result = llm_process(chunk["curr"], chunk["prev"])
        processed_chunks.append(result)
    print(processed_chunks)
    
    # Extract the 'curr' contents for TSCC object construction
    text_chunks = [chunk_dict["curr"] for chunk_dict in chunk_dicts]

    # Construct the TSCC object
    tscc = TSCC(
        uid=filename,  # Assuming filename is used as the UID
        processed=datetime.now(),
        model_used="model-v1",  # Replace with actual model name if applicable
        doc_loader_used=loader_choice,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        token_count=sum(len(chunk.split()) for chunk in text_chunks),
        chunks_generated=len(chunk_dicts),
        chunks=processed_chunks,
    )
    
    print("> DONE!\t")

    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time
    print(f"> [INFO]\tElapsed time: {elapsed_time:.2f}s")
    print(
        f"> [INFO]\tTime completed: {time.strftime('%m-%d %H:%M:%S', time.localtime())}"
    )

    return tscc
