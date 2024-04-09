CHUNK_SIZE = 1000
CHUNK_OVERLAP = 300
BROKEN_CHARS = {"\u2212": "-"}
LLM = {"dev": "gpt-3.5-turbo", "prod": "gpt-4-turbo-preview"}
PROMPT_TEMPLATE_1 = """
    Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words:
    
    "
    {curr_chunk}
"""
PROMPT_TEMPLATE_2 = """
    Step 1: Analyze this following previous chunk:
    "
    {prev_chunk}
    "
    
    Step 2: Adjust the following current chunk to fit with proper information flow:
    "
    {curr_chunk}
    "
"""