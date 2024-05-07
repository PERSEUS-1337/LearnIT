import json
import random
from models import Extracted
import paths
import os
import params

from tscc import tscc_process
from utils import (
    log_error,
    write_to_file,
    append_to_file,
    get_files_to_process,
    read_file_to_list,
    create_empty_file,
)


# Function to prepare directories and files
def prepare_directories_and_files(chunk_size, chunk_overlap):
    # Prepare Directories
    # output_file_path = os.path.join(paths.OUTPUT_PATH, f"{chunk_size}_{chunk_overlap}/")
    output_file_path = paths.OUTPUT_FINAL_TEST_PATH
    error_log_file = os.path.join(output_file_path, paths.ERROR_LOGS)
    id_log_file = os.path.join(output_file_path, paths.ID_LOGS)
    os.makedirs(output_file_path, exist_ok=True)

    # Prepare files
    create_empty_file(error_log_file)
    create_empty_file(id_log_file)
    files_to_process = read_file_to_list(paths.TEST_PARAMS_PATH)
    files_processed = read_file_to_list(id_log_file)

    return (
        output_file_path,
        error_log_file,
        id_log_file,
        files_to_process,
        files_processed,
    )


# Special function for parameter testing
def params_summarize_documents(chunk_size, chunk_overlap):
    # Prepare directories and files
    (
        output_file_path,
        error_log_file,
        id_log_file,
        files_to_process,
        files_processed,
    ) = prepare_directories_and_files(chunk_size, chunk_overlap)

    for i, file_name in enumerate(files_to_process):
        if file_name in files_processed:
            print(f"> [{i}]\t{file_name} - Already Processed!")
            continue

        print(f"\n> [{i}]\t{file_name} | CS: {chunk_size} | CO: {chunk_overlap}")
        file_path = os.path.join(paths.REFERENCES_PATH, file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            try:
                json_data = json.load(file)
                processed_content = tscc_process(
                    json_data, int(chunk_size), int(chunk_overlap)
                )
                extracted = Extracted(json_data["title"], processed_content)

                write_to_file(extracted, file_name, output_file_path)
                append_to_file(id_log_file, file_name)

            except Exception as e:
                # Log the error to the error log file
                log_error(file_name, str(e), error_log_file)

    print("> Processing complete.")


# Special function for parameter testing
def final_summarize_documents(chunk_size, chunk_overlap, filename):
    # Prepare directories and files
    (
        output_file_path,
        error_log_file,
        id_log_file,
        files_to_process,
        files_processed,
    ) = prepare_directories_and_files(chunk_size, chunk_overlap)
    
    files_to_process = read_file_to_list(os.path.join(paths.LOGS_PATH, filename))
    for i, file_name in enumerate(files_to_process):
        if file_name in files_processed:
            print(f"> [{i}]\t{file_name} - Already Processed!")
            continue

        print(f"\n> [{i}]\t{file_name} | CS: {chunk_size} | CO: {chunk_overlap}")
        file_path = os.path.join(paths.REFERENCES_PATH, file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            try:
                json_data = json.load(file)
                processed_content = tscc_process(
                    json_data, int(chunk_size), int(chunk_overlap)
                )
                extracted = Extracted(json_data["title"], processed_content)

                write_to_file(extracted, file_name, output_file_path)
                append_to_file(id_log_file, file_name)

            except Exception as e:
                # Log the error to the error log file
                log_error(file_name, str(e), error_log_file)

    print("> Processing complete.")


def summarize_documents(files_to_process):
    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")

    for file_name in files_to_process:
        print(f">Processing {file_name}")
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


def split_file():
    input_file = paths.TEST_FINAL_PATH
    # Read the contents of the input file
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Shuffle the lines
    random.shuffle(lines)

    # Calculate the number of lines in each part
    total_lines = len(lines)
    lines_per_part = total_lines // 4

    # Split the lines into four parts
    parts = [lines[i:i + lines_per_part] for i in range(0, total_lines, lines_per_part)]

    # Write each part into a separate file
    for i, part in enumerate(parts, start=1):
        output_file = os.path.join(paths.LOGS_PATH, f"part_{i}.txt")
        with open(output_file, 'w') as f:
            f.writelines(part)
        print(f"Part {i} saved to {output_file}")

def main():
    """Main Menu for testing purposes"""
    while True:
        print(
            "===========\nSummarize Datasets for TSCC Output ROUGE Testing\n==========="
        )
        print("[1] Summarize All Documents")
        print("[2] Testing: Summarize via Parameter Testing List")
        print("[3] Testing: Summarize via Final Test List")
        print("[4] Data: Split Final Test List")
        choice = input("> Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            files_to_process = get_files_to_process(paths.REFERENCES_PATH)
            summarize_documents(files_to_process)
        elif choice == "2":
            chunk_size = int(input("> Enter chunk_size: "))
            chunk_overlap = int(input("> Enter chunk_overlap: "))
            params_summarize_documents(chunk_size, chunk_overlap)
        elif choice == "3":
            chunk_size = int(input("> Enter chunk_size: "))
            chunk_overlap = int(input("> Enter chunk_overlap: "))
            filename = input("> Enter filename: ")
            final_summarize_documents(chunk_size, chunk_overlap, filename)
        elif choice == "4":
            split_file()
        else:
            print("> Invalid choice")


if __name__ == "__main__":
    main()
