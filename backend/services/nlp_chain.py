from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import re
import time
import cleantext
from typing import Optional, Tuple, List

import asyncio

from dotenv import dotenv_values, load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    PyPDFium2Loader,
    TextLoader,
    PyMuPDFLoader,
)

from fastapi import status

from middleware import apiMsg
from utils.fileUtils import update_user_doc_status
from models.document import TSCC, DocTokens, ProcessStatus
from utils.config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    LLM_TEMP,
    LLMS,
    PROMPT_MAIN,
    LOADERS,
)


config = dotenv_values(".env")

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def extract_page_content(chunk) -> str:
    """Extract page content from a chunk string."""
    match = re.search(r"page_content='(.*?)' metadata=", chunk, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def document_tokenizer_sync(
    file_path, doc_uid, loader_choice
) -> Tuple[DocTokens, List]:

    loader_choice = "default" if loader_choice is None else loader_choice

    if LOADERS[loader_choice] == "PyPDFLoader":
        loader = PyPDFLoader(file_path)
    elif LOADERS[loader_choice] == "PyPDFium2Loader":
        loader = PyPDFium2Loader(file_path)
    elif LOADERS[loader_choice] == "PyMuPDFLoader":
        loader = PyMuPDFLoader(file_path)
    elif LOADERS[loader_choice] == "TextLoader":
        loader = TextLoader(file_path)

    document = loader.load()

    start_time = time.time()
    print(f"> [TKZR]\t{doc_uid} - document_tokenizer()\n", end="", flush=True)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )

    pre_text_chunks = text_splitter.split_documents(document)

    # Directly clean and store the extracted page content in text_chunks
    text_chunks = [
        cleantext.clean(extract_page_content(str(chunk)), extra_spaces=True)
        for chunk in pre_text_chunks
        if extract_page_content(str(chunk)).strip()
    ]

    chunk_dicts = []
    for i in range(len(text_chunks)):
        chunk_dicts.append(
            {"prev": text_chunks[i - 1] if i > 0 else "", "curr": text_chunks[i]}
        )

    token_count = sum(len(chunk.split()) for chunk in text_chunks)
    chunk_count = len(chunk_dicts)

    doc_tokens = DocTokens(
        doc_uid=doc_uid,
        processed=datetime.now(),
        doc_loader_used=LOADERS[loader_choice],
        token_count=token_count,
        chunk_count=chunk_count,
        chunks=chunk_dicts,
    )

    print("> [TKZR]\tDONE!")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"> [TKZR]\tTime completed: {elapsed_time}s |  {time.strftime('%m-%d %H:%M:%S', time.localtime())}"
    )

    return doc_tokens, pre_text_chunks


async def document_tokenizer_async(
    file_path, doc_uid, loader_choice: Optional[str] = None
) -> str:
    """Asynchronous wrapper around document_tokenizer_sync"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as pool:
        future = loop.run_in_executor(
            pool, document_tokenizer_sync, file_path, doc_uid, loader_choice
        )
        return await future


### RAG RELATED FUNCTIONS
def setup_db(filename, chunks):

    persist_directory = f"db/rag/{filename}"

    embedding = OpenAIEmbeddings()

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()

    return persist_directory


def retrieve_db(db_dir):
    vectordb = Chroma.load(db_dir)
    return vectordb


def qa_chain_sync(query, db_dir, chosen_model):

    chosen_model = "default" if chosen_model is None else chosen_model

    db = Chroma(persist_directory=db_dir, embedding_function=OpenAIEmbeddings())
    turbo_llm = ChatOpenAI(temperature=0, model_name=LLMS[chosen_model])
    retriever = db.as_retriever(search_kwargs={"k": 6}, search_type="mmr")
    chain = RetrievalQA.from_chain_type(
        llm=turbo_llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    response = chain(query)
    return response


async def qa_chain_async(query, db_dir, chosen_model: Optional[str] = None) -> str:
    """Asynchronous wrapper around qa_chain_sync"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as pool:
        future = loop.run_in_executor(pool, qa_chain_sync, query, db_dir, chosen_model)
        return await future


### TSCC RELATED FUNCTIONS
def llm_process_sync(curr_chunk, prev_chunk, chosen_model) -> str:
    turbo_llm = ChatOpenAI(temperature=LLM_TEMP, model_name=LLMS[chosen_model])

    prompt = PromptTemplate.from_template(template=PROMPT_MAIN)
    llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
    response = llm_chain.invoke({"curr_chunk": curr_chunk, "prev_chunk": prev_chunk})
    return response["text"]


async def llm_process_async(curr_chunk, prev_chunk, chosen_model) -> str:
    """Asynchronous wrapper around llm_process_sync"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as pool:
        future = loop.run_in_executor(
            pool, llm_process_sync, curr_chunk, prev_chunk, chosen_model
        )
        return await future


async def generate_tscc(db, doc, user, filename, doc_tokens, chosen_model: Optional[str] = None) -> TSCC:
    chosen_model = "default" if chosen_model is None else chosen_model

    _id = str(doc_tokens["_id"])
    chunk_dicts = doc_tokens["chunks"]
    total_chunk_dicts = doc_tokens["chunk_count"]

    start_time = time.time()  # Record start time
    print(f"> [TSCC]\tDocument: {doc_tokens['_id']}")

    processed_chunks = []

    for i, chunk in enumerate(chunk_dicts, start=1):
        result = await llm_process_async(chunk["curr"], chunk["prev"], chosen_model)
        processed_chunks.append(result)
        print(f"> [TSCC]\t{i} / {total_chunk_dicts} processed")
        doc.process_status = ProcessStatus(code=status.HTTP_202_ACCEPTED, message=f"{i} / {total_chunk_dicts} processed")
        await update_user_doc_status(db, user, filename, doc)

    token_count = sum(len(chunk.split()) for chunk in processed_chunks)
    chunk_count = len(chunk_dicts)

    print("> [TSCC]\tDONE!")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"> [TSCC]\tTime completed: {elapsed_time}s |  {time.strftime('%m-%d %H:%M:%S', time.localtime())}"
    )

    tscc = TSCC(
        doc_uid=_id,
        processed=datetime.now(),
        process_time=elapsed_time,
        model_used=LLMS[chosen_model],
        token_count=token_count,
        chunk_count=chunk_count,
        chunks=processed_chunks,
    )

    return tscc
