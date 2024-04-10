import json
import os
import re
import paths
from models import ExtractedEncoder


def write_to_file(data, file_name, file_path=paths.OUTPUT_PATH):
    """Writes the data into a json formatted file for later processing by TSCC and other functions

    Args:
        data (str): Contains the text to be written to the json file
        file_name (str): Usually contains the id of the paper that is to be used as the file_name
        file_path (str, optional): The location of which the file is to be stored. Defaults to paths.OUTPUT_PATH.
    """

    output_path = os.path.join(file_path, file_name)
    with open(output_path, "w") as file:
        json.dump(data, file, cls=ExtractedEncoder, indent=4)
    print(f"File saved - {file_name}")
    

def log_error(file_name, error_msg, error_log_file):
    """Log errors to a file

    Args:
        file_name (str): The file that caused the error
        error_msg (str): The error that the file spit out
        error_log_file (str): The file of which to append the error to
    """
    with open(error_log_file, "a") as log_file:
        log_file.write(f"Error processing {file_name}: {error_msg}\n")
        

def get_files_to_process(folder_path) -> list:
    """Returns a list of files from a specified folder

    Args:
        folder_path (str): Folder where the files are located

    Returns:
        list: A list of files to feed into the loop
    """
    files = os.listdir(folder_path)
    return files

if __name__ == "__main__":
    get_files_to_process(paths.REFERENCES_PATH)