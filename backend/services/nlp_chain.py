from datetime import datetime
import os
import re
import time

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

from models.document import TSCC, DocTokens
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


def document_tokenizer(file_path, loader_choice="PyPDFium2Loader") -> DocTokens:
    # file_path = os.path.join(config["UPLOAD_PATH"], filename)

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

    token_count = sum(len(chunk.split()) for chunk in text_chunks)
    chunk_count = len(chunk_dicts)

    doc_tokens = DocTokens(
        processed=datetime.now(),
        doc_loader_used=loader_choice,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        token_count=token_count,
        chunk_count=chunk_count,
        chunks=chunk_dicts,
    )

    return doc_tokens


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
    response = llm_chain.invoke({"curr_chunk": curr_chunk, "prev_chunk": prev_chunk})
    return response["text"]


def generate_tscc(document, chosen_model=LLMS["dev"]) -> TSCC:
    # Save properties for later
    _id = document["_id"]
    loader_choice = document["doc_loader_used"]
    chunk_dicts = document["chunks"]

    start_time = time.time()  # Record start time
    print(f"> [PROCESS]\t{document['_id']} - TSCC():\n", end="", flush=True)

    # Go through the whole chunk list and one by one pass to LLM
    processed_chunks = []
    for chunk in chunk_dicts:
        result = llm_process(chunk["curr"], chunk["prev"], chosen_model)
        processed_chunks.append(result)

    token_count = sum(len(chunk.split()) for chunk in processed_chunks)
    chunk_count = len(chunk_dicts)

    # Construct the TSCC object
    tscc = TSCC(
        processed=datetime.now(),
        model_used=chosen_model,  # Replace with actual model name if applicable
        doc_loader_used=loader_choice,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        token_count=token_count,
        chunk_count=chunk_count,
        chunks=processed_chunks,
    )

    print("> DONE!\t")

    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time
    print(
        f"> [INFO]\tTime completed: {elapsed_time}s |  {time.strftime('%m-%d %H:%M:%S', time.localtime())}"
    )

    return tscc
