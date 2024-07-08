DEFAULT_CHUNK_SIZE = 1000
CHUNK_SIZE_LIST = [750, 1000, 1250, 1500]
DEFAULT_CHUNK_OVERLAP = 100
CHUNK_OVERLAP_LIST = [100, 200, 300]
LLM_TEMP = 0.5
LLMS = {"dev": "gpt-3.5-turbo", "prod": "gpt-4o"}
LOADERS = {
    "default": "PyMuPDFLoader",
    "0": "TextLoader",
    "1": "PyPDFLoader",
    "2": "PyPDFium2Loader",
    "3": "PyMuPDFLoader",
}
PROMPT_MAIN = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1 - Extractively Summarize the following text, try to preserve key details, and condense the text by removing irrelevant words:
    
    "
    {curr_chunk}
    "
    
    Step 2 - To assist you with the task, here is the context of the paragraphs before it, to give you an idea on the information flow, and it is contained in the following text.:
    
    "
    {prev_chunk}
    "
    
    Step 3: Make sure that the prev_chunk and curr_chunk is not redundant with words, and ideas. Both should at least be distinct as they are separate text chunks
    
    Step 4: Output the summarized chunk
"""
