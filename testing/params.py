DEFAULT_CHUNK_SIZE = 1000
CHUNK_SIZE_LIST = [1000]
DEFAULT_CHUNK_OVERLAP = 200
CHUNK_OVERLAP_LIST = [100]
LLM_TEMP = 0
LLMS = {"dev": "gpt-3.5-turbo", "prod": "gpt-4-turbo-preview"}
PROMPT_MAIN = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1 - Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words:
    
    "
    {curr_chunk}
    "
    
    Step 2 - To assist you with the task, here is the context of the paragraphs before it, to give you an idea on the information flow, and it is contained here in this prev_chunk:
    
    "
    {prev_chunk}
    "
    
    Step 3: Make sure that the prev_chunk and curr_chunk is not redundant with words, and ideas. Both should at least be distinct as they are separate text chunks
    
    Step 4: Output the summarized chunk
"""
PROMPT_2_1 = """
    Extractively Summarize the following text, by preserving key details, and condensing the text by removing irrelevant words:
    
    "
    {curr_chunk}
    "
    
    Step 2: Output the summarized chunk
"""
PROMPT_2_2 = """
    Step 1: Analyze the following chunk labeled as "curr_chunk" that you will be adjusting:
    
    "
    {curr_chunk}
    "
    
    Step 2: Analyze the following text chunk, which is labeled as "prev_chunk" to reduce any redundant context that is included with the "curr_chunk" that you just have analyzed:
    
    "
    {prev_chunk}
    "
    
    Step 3: Output the summarized chunk
    
"""
