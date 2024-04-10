import os
import json
import sys

from models import Document, Extracted, ExtractedEncoder
import paths
import params
from utils import log_error, write_to_file

# Create output directories if they don't exist
os.makedirs(paths.REFERENCES_PATH, exist_ok=True)
os.makedirs(paths.SUMMARIES_PATH, exist_ok=True)

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


##### GOV REPORT FUNCTIONS
def extract_list(data, label):
    """Simply gets the list of text,and ombines them into a single string

    Args:
        data (dict): contains the text to be extracted
        label (str): determines where to extract from the dict

    Returns:
        str: all of the entries combined into a single string
    """
    entries = data[label]
    combined_str = " ".join(entries)
    return combined_str


def extract_paragraphs(subsections):
    """Recursively extract paragraphs from the subsections of the document

    Args:
        subsections (dict): these are nested dicts containing the paragraphs that may have sub-sections to them

    Returns:
        list: all of the paragraphs combined
    """
    paragraphs = []
    for subsection in subsections:
        paragraphs.extend(subsection["paragraphs"])
        # Recursively extract paragraphs from nested subsections
        paragraphs.extend(extract_paragraphs(subsection["subsections"]))
    return paragraphs


def extract_reference_paragraphs(json_data):
    """Extract the paragraphs of the text that pertains to the reference text, and combine them to a single stirng

    Args:
        json_data (dict): contains the text to be extracted

    Returns:
        str: all of the references combined into a single string
    """

    # Extract paragraphs from the top-level subsections
    paragraphs = extract_paragraphs(json_data["reports"]["subsections"])
    # Combine all paragraphs into a single string
    combined_paragraphs = " ".join(paragraphs)
    return combined_paragraphs


##### UNIVERSAL FUNCTIONS
def process_json(file_path, type, flag=False) -> Document:
    """Process the json and return relevant Document object format

    Args:
        file_path (str): either contains actual file path, or json (dict)
        type (str): choose between BILL, GOVR, or SCI

    Returns:
        Document: A document object containing the extracted text, along with its relevant properties
    """
    if type == "BILL":
        json_data = json.loads(file_path)
        summary = json_data["summary"]
        reference = json_data["text"]
        return Document(json_data["bill_id"], json_data["title"], reference, summary)

    if type == "SCI_ref":
        json_data = json.loads(file_path)
        reference = extract_list(json_data, "source")

        if flag:
            return Document(json_data["paper_id"], json_data["paper_id"], reference)
        return Document(json_data["paper_id"], json_data["paper_id"], reference, None)

    if type == "SCI_sum":
        json_data = json.loads(file_path)
        summary = extract_list(json_data, "source")
        return Document(json_data["paper_id"], json_data["title"], None, summary)

    if type == "GOVR":
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            summary = extract_list(json_data, "summary")
            reference = extract_reference_paragraphs(json_data)
            return Document(json_data["id"], json_data["title"], reference, summary)


def extract_gov_report_dataset():
    """Function for extracting from the GovReport dataset"""

    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")
    files_to_process = os.listdir(paths.GOV_REPORT_PATH)

    # Iterate over JSON files in the folder
    for file_name in files_to_process:
        try:
            file_path = os.path.join(paths.GOV_REPORT_PATH, file_name)

            data = process_json(file_path, "GOVR")

            write_to_file(data.reference, f"GOVR_{data.id}.json", paths.REFERENCES_PATH)
            write_to_file(data.summary, f"GOVR_{data.id}.json", paths.SUMMARIES_PATH)

            print(f"- Done - {file_name}")

        except Exception as e:
            # Log the error to the error log file
            log_error(file_name, str(e), error_log_file)

    print("Extraction complete.")


def extract_bill_sum_dataset():
    """Function for extracting from the BillSum dataset"""
    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")

    input_files = [
        "ca_test_data_final_OFFICIAL.jsonl",
        "us_test_data_final_OFFICIAL.jsonl",
        "us_train_data_final_OFFICIAL.jsonl",
    ]

    # Read the JSONL files line by line
    for input_file in input_files:
        print(f"Processing {input_file}")

        with open(os.path.join(paths.BILL_SUM_PATH, input_file), "r") as infile:
            for line in infile:
                try:
                    data = process_json(line, "BILL")

                    write_to_file(
                        data.reference, f"BILL_{data.id}.json", paths.REFERENCES_PATH
                    )
                    write_to_file(
                        data.summary, f"BILL_{data.id}.json", paths.SUMMARIES_PATH
                    )

                    print(f"- Done - {data.title}")

                except Exception as e:
                    # Log the error to the error log file
                    log_error(file_name, str(e), error_log_file)

    print("Extraction complete.")


def extract_sci_tldr_dataset():
    """Function for extracting from the SciTLDR dataset"""

    error_log_file = os.path.join(paths.LOGS_PATH, "error_logs.txt")

    refs_to_process = os.listdir(paths.SCI_TLDR_REF_PATH)
    sums_to_process = os.listdir(paths.SCI_TLDR_SUM_PATH)

    # Read reference files first
    for file_name in refs_to_process:
        print(f"Processing {file_name}")

        with open(os.path.join(paths.SCI_TLDR_REF_PATH, file_name), "r") as infile:
            for line in infile:
                try:
                    # Because of a bug in the train.jsonl file in the Reference set, the title is not included with the data, only its paper-id
                    if file_name != "train.jsonl":
                        data = process_json(line, "SCI_ref", False)
                    else:
                        data = process_json(line, "SCI_ref", True)

                    write_to_file(
                        data.reference, f"SCI_{data.id}.json", paths.REFERENCES_PATH
                    )

                    print(f"- Done - {data.title}")

                except Exception as e:
                    # Log the error to the error log file
                    log_error(file_name, str(e), error_log_file)

    for file_name in sums_to_process:
        print(f"Processing {file_name}")
        with open(os.path.join(paths.SCI_TLDR_SUM_PATH, file_name), "r") as infile:
            for line in infile:
                try:
                    data = process_json(line, "SCI_sum")

                    write_to_file(
                        data.summary, f"BILL_{data.id}.json", paths.SUMMARIES_PATH
                    )

                    print(f"- Done - {data.id}")

                except Exception as e:
                    # Log the error to the error log file
                    log_error(file_name, str(e), error_log_file)

    print("Extraction complete.")


def main():
    """Main Menu for testing purposes"""
    while True:
        print("Extract Dataset Summaries\n===========")
        print("1. Extract data from the BillSum dataset")
        print("2. Extract data from the GovReport dataset")
        print("3. Extract data from the SciTLDR dataset")
        choice = input("Enter your choice: ")
        if choice == "0":
            break
        elif choice == "1":
            extract_bill_sum_dataset()
            # extract_dataset("BILL")
        elif choice == "2":
            extract_gov_report_dataset()
            # extract_dataset("GOVR")
        elif choice == "3":
            extract_sci_tldr_dataset()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
