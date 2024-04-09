CHUNK_SIZE = 1000
CHUNK_OVERLAP = 250
BROKEN_CHARS = {"\u2212": "-"}
LLM = {"dev": "gpt-3.5-turbo", "prod": "gpt-4-turbo-preview"}
PROMPT_TEMPLATE = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1 - Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words:
    
    "
    {curr_chunk}
    "
    
    Step 2 - To assist you with the task, here is the context of the text before it, to give you an idea on the information flow, and it is contained here in this prev_chunk:
    
    "
    {prev_chunk}
    "
    
    Step 4: Make sure that the prev_chunk and curr_chunk is not redundant with words, and ideas. Both should at least be distinct as they are separate text chunks
    
    Step 5: Output the summarized chunk
"""