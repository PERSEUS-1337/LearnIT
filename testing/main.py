import os
import json
import params
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    PyPDFium2Loader,
    TextLoader,
    PyMuPDFLoader,
)
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, RetrievalQA


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")


def process_document(file, size, overlap, loader_choice):
    # Append the file string to "./datasets/downloaded_documents"
    file_path = os.path.join("./datasets/downloaded_documents", file)

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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    text_chunks = text_splitter.split_documents(document)

    print(json.dumps(str(text_chunks)))

    # print(len(text_chunks))
    prev_chunk = ""
    for i, chunk in enumerate(text_chunks):
        chunk.metadata["index"] = i
        chunk.metadata["prev_chunk"] = prev_chunk
        # print(f"{i}: {chunk.page_content}\n")
        prev_chunk = chunk.page_content
        # chunk.metadata["global"] = document

    return text_chunks


def process_llm_response(llm_response):
    print(f"Result:\n{llm_response['result']}")
    print("\nSources:")
    for source in llm_response["source_documents"]:
        #     print(f"{source.metadata['source']}, pg. {source.metadata['page']}")
        print(f"{source.metadata}")


def setup_db(chunks, file):
    # We then create the DB
    # Supply the directory, which is /db, where we will embed and store the texts
    persist_directory = (
        f"db_directory/{file}"  # Use the document name as part of the db_directory
    )

    embedding = OpenAIEmbeddings()

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    vectordb.persist()

    return vectordb


def setup_chain(db, chosen_model):
    # Set up the turbo LLM
    HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    repo_id = "microsoft/phi-1_5"
    # hf_llm = HuggingFaceEndpoint(
    #     repo_id=repo_id, max_length=128, temperature=0.5, token=HUGGINGFACEHUB_API_TOKEN
    # )
    turbo_llm = ChatOpenAI(temperature=0, model_name=chosen_model)
    retriever = db.as_retriever(search_kwargs={"k": 10})
    chain = RetrievalQA.from_chain_type(
        llm=turbo_llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return chain


def qa_chain_setup(text, model, file):
    db = setup_db(text, file)
    chain = setup_chain(db, model)
    return chain


def llm_qa_response(chain, query):
    llm_response = chain(query)
    process_llm_response(llm_response)
    return llm_response


def llm_process(chunk, chosen_model):
    # Set up the turbo LLM
    # turbo_llm = OpenAI(temperature=0, model_name=chosen_model)
    turbo_llm = ChatOpenAI(temperature=0.7, model_name=chosen_model)

    # Create a PromptTemplate instance
    prompt = PromptTemplate.from_template(template=params.PROMPT_MAIN)

    llm_chain = LLMChain(prompt=prompt, llm=turbo_llm)
    return llm_chain.run(
        {
            "prev_chunk": chunk.metadata["prev_chunk"],
            "curr_chunk": chunk.page_content,
        }
    )
