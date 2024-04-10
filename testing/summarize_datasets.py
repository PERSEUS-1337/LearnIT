import json
from models import Extracted, ExtractedEncoder
import paths
import os
import params

from tscc import tscc_process
from utils import log_error, write_to_file, append_to_json, get_files_to_process, read_file_to_list

# Special function for parameter testing
def params_summarize_documents(files_to_process, chunk_size_list, chunk_overlap_list):
    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")
    
    for chunk_size in chunk_size_list:
        for chunk_overlap in chunk_overlap_list:
            output_file = os.path.join(paths.OUTPUT_PATH, f"{chunk_size}_{chunk_overlap}.jsonl")

            for file_name in files_to_process:
                print(f"Processing {file_name} with chunk size {chunk_size} and overlap {chunk_overlap}")
                file_path = os.path.join(paths.REFERENCES_PATH, file_name)

                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        json_data = json.load(file)
                        processed_content = tscc_process(json_data, int(chunk_size), int(chunk_overlap))
                        extracted = Extracted(json_data["title"], processed_content)
                        # print(extracted)
                        # Append the extracted content to the JSONL file
                        with open(output_file, "a", encoding="utf-8") as outfile:
                            json.dump(extracted, outfile, cls=ExtractedEncoder)
                            outfile.write("\n")  # Add newline between JSON objects
                        # append_to_json(output_file, extracted)

                    except Exception as e:
                        # Log the error to the error log file
                        log_error(file_name, str(e), error_log_file)

    print("Processing complete.")



def summarize_documents(files_to_process):
    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")

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
        print("===========\nSummarize Datasets for TSCC Output ROUGE Testing\n===========")
        print("[1] Summarize All Documents")
        print("[2] Testing: Summarize via Parameter Testing List")
        print("[3] Testing: Summarize via Final Test List")
        choice = input("Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            files_to_process = get_files_to_process(paths.REFERENCES_PATH)
            summarize_documents(files_to_process)
        elif choice == "2":
            files_to_process = read_file_to_list(paths.TEST_PARAMS_PATH)
            params_summarize_documents(files_to_process, params.CHUNK_SIZE_LIST, params.CHUNK_OVERLAP_LIST)
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
