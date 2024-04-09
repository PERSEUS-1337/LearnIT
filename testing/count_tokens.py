import os
import json
from collections import Counter
from nltk.tokenize import word_tokenize
import paths

def count_tokens_in_folder(folder_path):
    """Iterates over json files to count the total number of tokens

    Args:
        folder_path (str): Accepts a folder string that contains files to be processed
    """
    token_count = Counter()

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the file is a JSON file
        if file_name.endswith('.json'):
            with open(file_path, 'r') as file:
                # Load JSON content
                data = json.load(file)
                content = data.get('content', '')

                # Tokenize content
                tokens = word_tokenize(content)

                # Update token count
                token_count.update(tokens)
                print(f"Done - {file_name}")
                
    total_token_count = sum(token_count.values())
    file_count = len(os.listdir(folder_path))

    # Get folder name
    folder_name = os.path.basename(folder_path)

    # Save token counts to a text file
    output_file = f"{paths.LOGS_PATH}/{folder_name}_token_count.txt"
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(f"Total Token Count for {folder_name}: {sum(token_count.values())}\n")
        outfile.write(f"File Count: {file_count}\n\n")
        outfile.write("Bag of Words:\n=====\n")
        for token, count in sorted(token_count.items(), key=lambda x: x[1], reverse=True):
            outfile.write(f"{token} = {count}\n")

def main():
    folder_paths = [paths.REFERENCES_PATH, paths.SUMMARIES_PATH]
    
    """Main Menu for testing purposes"""
    while True:
        print("\nCount Total Tokens of Folders\n===========")
        print("1. Process References")
        print("2. Process Summaries")
        print("3. Process all in folder_paths list")
        choice = input("Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            count_tokens_in_folder(paths.REFERENCES_PATH)
        elif choice == "2":
            count_tokens_in_folder(paths.SUMMARIES_PATH)
        elif choice == "3":
            for folder_path in folder_paths:
                count_tokens_in_folder(folder_path)
        elif choice == "69":
            count_tokens_in_folder("./extracted_data/test")
        else:
            print("Invalid choice")
            

if __name__ == "__main__":
    main()