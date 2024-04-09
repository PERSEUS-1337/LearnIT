CHUNK_SIZE = 1000
CHUNK_OVERLAP = 250
BROKEN_CHARS = {"\u2212": "-"}
LLM = {"dev": "gpt-3.5-turbo", "prod": "gpt-4-turbo-preview"}
PROMPT_TEMPLATE_TEST = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1: Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words
    
    {curr_chunk}

    Step 2: After processing the curr_chunk, use the prev_chunk to adjust your output accordingly, and to ensure there is proper information flow for user reading. But try not to add information from the prev_chunk to the curr_chunk to reduce redundancy
    
    {prev_chunk}

    Step 2: Output the condensed chunk
"""
PROMPT_TEMPLATE = """
    Follow the steps to provide a condensed text chunk:
    
    Step 1: Analyze the prev_chunk to gain an idea on how to follow up with generating the summarization of the curr_chunk
    
    {prev_chunk}

    Step 2: After reading that, you will now Extractively Summarize the curr_chunk, try to preserve key details, and condense the text by removing irrelevant words, with the help of what the context of the prev_chunk was
    
    {curr_chunk}

    Step 3: Output the condensed chunk
"""
