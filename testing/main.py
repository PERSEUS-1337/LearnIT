import os
from dotenv import load_dotenv

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, PyPDFium2Loader, TextLoader
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, RetrievalQA

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def process_document(file, size, overlap, loader_choice):
    # Append the file string to "./documents"
    file_path = os.path.join("./documents", file)

    # Initialize PyPDFLoader with the file path
    if loader_choice == "PyPDFLoader":
        loader = PyPDFLoader(file_path)
    elif loader_choice == "PyPDFium2Loader":
        loader = PyPDFium2Loader(file_path)
    elif loader_choice == "TextLoader":
        loader = TextLoader(file_path)

    document = loader.load()
    print(document)

    # Split texts into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    text_chunks = text_splitter.split_documents(document)

    print(len(text_chunks))
    prev_chunk = ""
    for i, chunk in enumerate(text_chunks):
        chunk.metadata["index"] = i
        chunk.metadata["prev_chunk"] = prev_chunk
        print(f"{i}: {chunk.page_content}\n")
        prev_chunk = chunk.page_content

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
    turbo_llm = ChatOpenAI(temperature=0, model_name=chosen_model)

    # Create a proper prompt template
    # prompt_template = PromptTemplate.from_template(
    #     """
    #     You are a very good summarizer, which aims to reduce the length of the text, without sacrificing much information.
    #
    #     You are given a chunk of text that you will be summarizing and condensing, to help the user read better and faster.
    #
    #     To help you have a better understanding on how to condense the text that will be given, you are provided a context of the previous words before the current text that you will be condensing, and it is the following: {prev_chunk}.
    #
    #     Using the context from the previous chunk that you already have, and the title of the paper, you will now use it to aid your condensing of the following text, and this is the only thing that you will reply back, once you have condensed it: {curr_chunk}. Make sure to, again, retain as much information as possible, while trying to reduce the word count even further, only retaining the most important information in the chunk.
    #     """
    # )
    prompt_template = PromptTemplate.from_template(
        """
        You are a very good summarizer. You will not be adding things to the text such as "the article discusses" or "the text says".
        Stay true to the text.
        
        Condense the following text while retaining as much crucial detail as you can: {curr_chunk}
        
        Use the following previous chunk as context on how to condense the current chunk: {prev_chunk}
        """
    )

    llm_chain = LLMChain(prompt=prompt_template, llm=turbo_llm)
    return llm_chain.run(
        {
            "prev_chunk": chunk.metadata["prev_chunk"],
            "curr_chunk": chunk.page_content,
        }
    )

    # for i, chunk in enumerate(chunks):
    #     print(
    #         llm_chain.run(
    #             {
    #                 "prev_chunk": chunk.metadata["prev_chunk"],
    #                 "curr_chunk": chunk.page_content,
    #             }
    #         )
    #     )
