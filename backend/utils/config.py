DEFAULT_CHUNK_SIZE = 1000
CHUNK_SIZE_LIST = [750, 1000, 1250, 1500]
DEFAULT_CHUNK_OVERLAP = 100
CHUNK_OVERLAP_LIST = [100, 200, 300]
LLM_TEMP = 0.5
LLMS = {"default": "gpt-3.5-turbo", "dev": "gpt-3.5-turbo", "prod": "gpt-4o"}
LOADERS = {
    "default": "PyMuPDFLoader",
    "0": "TextLoader",
    "1": "PyPDFLoader",
    "2": "PyPDFium2Loader",
    "3": "PyMuPDFLoader",
}
PROMPT_MAIN = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1 - Extractively Summarize the following text, try to preserve key details, important persons, statistics, keywords, and condense the text by removing irrelevant words and ideas:
    
    "
    {curr_chunk}
    "
    
    Step 2 - To assist you with the task, here is the context of the paragraphs before it, to give you an idea on the information flow, and it is contained in the following text:
    
    
    {prev_chunk}
    
    
    Step 4: Output ONLY the summarized chunk
"""
