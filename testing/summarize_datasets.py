import json
from models import Extracted
import paths
import os

from tscc import tscc_process
from utils import log_error, write_to_file, get_files_to_process

def summarize_documents():

    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")
    
    files_to_process = get_files_to_process(paths.REFERENCES_PATH)

    
    for file_name in files_to_process:
        print(f"Processing {file_name}")
        file_path = os.path.join(paths.REFERENCES_PATH, file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            try:
                json_data = json.load(file)
                processed_content = tscc_process(json_data)
                extracted = Extracted(json_data["title"], processed_content)
                write_to_file(extracted, file_name, paths.OUTPUT_PATH)

            except Exception as e:
                # Log the error to the error log file
                log_error(file_name, str(e), error_log_file)



def main():
    """Main Menu for testing purposes"""
    while True:
        print("\Summarize Datasets for TSCC Output ROUGE Testing\n===========")
        choice = input("Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            summarize_documents()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()