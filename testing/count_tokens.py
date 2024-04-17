import os
import json
from collections import Counter
from nltk.tokenize import word_tokenize
import paths


def calculate_token_reduction(ref_tokens, gen_tokens):
    """Calculates the reduction in percentage of tokens.

    Args:
        ref_tokens (int): Total number of tokens in the reference data.
        gen_tokens (int): Total number of tokens in the generated data.

    Returns:
        float: Reduction in percentage of tokens.
    """
    reduction_percentage = ((ref_tokens - gen_tokens) / ref_tokens) * 100
    return reduction_percentage


def count_tokens_in_data(data):
    """Counts the total number of tokens in a single data.

    Args:
        data (str): Dictionary containing the data to be processed.

    Returns:
        int: Total number of tokens in the data.
    """
    tokens = word_tokenize(data)
    token_count = len(tokens)
    return token_count


def count_tokens_in_folder(folder_path):
    """Iterates over json files to count the total number of tokens

    Args:
        folder_path (str): Accepts a folder string that contains files to be processed
    """
    total_token_count = 0

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is a JSON file
        if file_name.endswith(".json"):
            with open(file_path, "r") as file:
                # Load JSON content
                data = json.load(file)

                # Count tokens in the data
                token_count = count_tokens_in_data(data)
                total_token_count += token_count
                print(f"Done - {file_name}")

    file_count = len(os.listdir(folder_path))

    # Get folder name
    folder_name = os.path.basename(folder_path)

    # Save token counts to a text file
    output_file = f"{paths.LOGS_PATH}/{folder_name}_token_count.txt"
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(f"Total Token Count for {folder_name}: {total_token_count}\n")
        outfile.write(f"File Count: {file_count}\n")


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
