import json
import os
import random
import paths
import datetime
from models import ExtractedEncoder


import os


def create_empty_file(file_path):
    """Creates an empty file if it doesn't already exist.

    Args:
        file_path (str): The path of the file to be created.
    """
    if not os.path.exists(file_path):
        # Open the file in write mode to create it
        with open(file_path, "w"):
            pass  # This will create an empty file
        print(f"> Created Empty File - [{file_path}]")
    else:
        print(f"> File already exists - [{file_path}]")


def write_to_file(data, file_name, file_path=paths.OUTPUT_PATH):
    """Writes the data into a json formatted file for later processing by TSCC and other functions

    Args:
        -  data (str): Contains the text to be written to the json file
        - file_name (str): Usually contains the id of the paper that is to be used as the file_name
        - file_path (str, optional): The location of which the file is to be stored. Defaults to paths.OUTPUT_PATH.
    """

    output_path = os.path.join(file_path, file_name)
    with open(output_path, "w") as file:
        json.dump(data, file, cls=ExtractedEncoder, indent=4)
    print(f"> [SAVE] {file_name}")


def append_to_json(output_file, data):
    # Append the extracted content to the JSONL file
    with open(output_file, "a", encoding="utf-8") as outfile:
        json.dump(data, outfile, cls=ExtractedEncoder)
        outfile.write("\n")  # Add newline between JSON objects
    print(f"> [UPDATE] {output_file}")


def append_to_file(output_file, data):
    """Append the extracted content to the file

    Args:
        output_file (str): File to write on
        data (str): Text to be written
    """

    with open(output_file, "a", encoding="utf-8") as outfile:
        outfile.write(f"{data}\n")  # Add newline
    print(f"> [UPDATE] {output_file}")


def log_error(file_name, error_msg, error_log_file):
    """Log errors to a file with timestamp

    Args:
        - file_name (str): The file that caused the error
        - error_msg (str): The error message
        - error_log_file (str): The file to append the error message to
    """
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append the error message with the timestamp to the log file
    with open(error_log_file, "a") as log_file:
        log_file.write(f"[{timestamp}] Error processing {file_name}: {error_msg}\n")
    print(f"> [ERROR][{timestamp}] {file_name} - logged to {error_log_file}")


def get_files_to_process(folder_path) -> list:
    """Returns a list of files from a specified folder

    Args:
        - folder_path (str): Folder where the files are located

    Returns:
        - list: A list of files to feed into the loop
    """
    files = os.listdir(folder_path)
    return files


def generate_id_list(folder_path, n):
    """Generates two files
    - Randomly Selected Files for Parameter Testing
    - Remaining Non-Selected files for Final Testing

    Args:
        - folder_path (str): Path to the folder containing the files.
        - n (int): Number of files to select randomly.
    """
    random_output_file = os.path.join(paths.LOGS_PATH, "params_test.txt")
    final_output_file = os.path.join(paths.LOGS_PATH, "final_test.txt")

    # Get the list of files in the folder
    files = os.listdir(folder_path)

    # Check if n is greater than the total number of files
    n = min(n, len(files))

    # Randomly select n files
    random_files = random.sample(files, n)

    # Write the selected file names to the random output text file
    with open(random_output_file, "w") as f_random:
        for file_name in random_files:
            f_random.write(file_name + "\n")

    # Write the remaining file names to the final output text file
    with open(final_output_file, "w") as f_final:
        for file_name in files:
            if file_name not in random_files:
                f_final.write(file_name + "\n")

    print("> Done Generating List of Files for testing")


def read_file_to_list(file_path):
    """
    Reads a text file and converts its contents to a list.

    Args:
        file_path (str): The path to the text file.

    Returns:
        list: A list containing the lines of the text file.
    """
    # Initialize an empty list to store the file contents
    file_list = []

    # Read the contents of the text file
    with open(file_path, "r") as file:
        # Split the content by newline characters to get a list of lines
        file_list = file.read().strip().split("\n")

    print(f"> [{file_path}] Done reading and creating a list of files")
    return file_list


def append_statistics_to_json(
    file_path, title, rouge_scores, ref_tokens, gen_tokens, reduction_percentage
):
    """Append statistics to a JSON file.

    Args:
        file_path (str): The file path of the JSON file.
        title (str): The title of the data.
        rouge_scores (dict): Dictionary containing ROUGE scores.
        ref_tokens (int): Total number of tokens in the reference data.
        gen_tokens (int): Total number of tokens in the generated data.
        reduction_percentage (float): Reduction in percentage of tokens.
    """
    # Create dictionary with statistics
    statistics = {
        "title": title,
        "rouge_scores": rouge_scores,
        "ref_tokens": ref_tokens,
        "gen_tokens": gen_tokens,
        "reduction_percentage": reduction_percentage,
    }

    # Append statistics to JSON file
    with open(file_path, "a") as json_file:
        json.dump(statistics, json_file)
        json_file.write("\n")


if __name__ == "__main__":
    """Main Menu for testing purposes"""
    while True:
        print("===========\nUtils\n===========")
        print("[1] get_files_to_process()")
        print("[2] generate_id_list()")
        choice = input("\n> Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            get_files_to_process(paths.REFERENCES_PATH)
        elif choice == "2":
            n = int(input("> Enter sample size: "))
            generate_id_list(paths.REFERENCES_PATH, n)
        else:
            print(">Invalid choice")
