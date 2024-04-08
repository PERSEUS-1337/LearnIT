CHUNK_SIZE = 1000
CHUNK_OVERLAP = 250
BROKEN_CHARS = {"\u2212": "-"}
LLM = {"dev": "gpt-3.5-turbo", "prod": "gpt-4-turbo-preview"}
PROMPT_TEMPLATE = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1: Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words
    
    {curr_chunk}

    Step 2: After processing the curr_chunk, use the prev_chunk to adjust your output accordingly, and to ensure there is proper information flow for user reading
    
    {prev_chunk}

    Step 3: Output the condensed chunk itself
"""
