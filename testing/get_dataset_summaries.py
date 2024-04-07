import os
import json
import sys

from models import Document, Extracted, ExtractedEncoder
import paths
import params

# Create output directories if they don't exist
os.makedirs(paths.REFERENCES_PATH, exist_ok=True)
os.makedirs(paths.SUMMARIES_PATH, exist_ok=True)

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


##### GOV REPORT FUNCTIONS
def extract_summary(json_data):
    """Simply gets the summaries, and if there are multiple, combines them into a single string

    Args:
        json_data (dict): contains the text to be extracted

    Returns:
        str: all of the summaries combined into a single string
    """

    # Extract all summaries and combine them into a single sting
    summaries = json_data["summary"]
    combined_summary = " ".join(summaries)
    return combined_summary


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
def process_json(file_path, type) -> Document:
    """Process the json and return relevant Document object format

    Args:
        file_path (str): either contains actual file path, or json (dict)
        type (str): choose between BILL, GOVR, BOOK, or SCI

    Returns:
        Document: A document object containing the extracted text, along with its relevant properties
    """
    if type == "BILL":
        json_data = json.loads(file_path)
        summary = json_data["summary"]
        reference = json_data["text"]
        return Document(json_data["bill_id"], json_data["title"], reference, summary)

    elif type == "GOVR":
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            summary = extract_summary(json_data)
            reference = extract_reference_paragraphs(json_data)
            return Document(json_data["id"], json_data["title"], reference, summary)


def write_to_file(ref_data, sum_data, type, id):
    """
    Write data to a JSON file.

    Args:
        data (Extracted): Data to write to the file.
        output_file (str): Path to the output file.
    """
    ref_out_path = os.path.join(paths.REFERENCES_PATH, f"{type}{id}.json")
    with open(ref_out_path, "w") as file:
        json.dump(ref_data, file, cls=ExtractedEncoder, indent=4)

    sum_out_path = os.path.join(paths.SUMMARIES_PATH, f"{type}{id}.json")
    with open(sum_out_path, "w") as file:
        json.dump(sum_data, file, cls=ExtractedEncoder, indent=4)


def extract_gov_report_dataset():
    """Function for extracting from the GovReport dataset"""

    error_log_file = os.path.join(paths.ERROR_LOGS_PATH, "error_logs.txt")
    files_to_process = os.listdir(paths.GOV_REPORT_PATH)

    # Iterate over JSON files in the folder
    for file_name in files_to_process:
        try:
            file_path = os.path.join(paths.GOV_REPORT_PATH, file_name)

            data = process_json(file_path, "GOVR")

            reference_data = data.reference

            summary_data = data.summary

            write_to_file(reference_data, summary_data, "GOVR_", data.id)

            print(f"- Done - {data.title}")

        except Exception as e:
            # Log the error to the error log file
            with open(error_log_file, "a") as log_file:
                log_file.write(f"Error processing {file_name}: {str(e)}\n")

    print("Extraction complete.")


def extract_bill_sum_dataset():
    """Function for extracting from the BillSum dataset"""

    input_files = [
        "ca_test_data_final_OFFICIAL.jsonl",
        "us_test_data_final_OFFICIAL.jsonl",
        "us_train_data_final_OFFICIAL.jsonl",
    ]

    error_log_file = os.path.join(paths.ERROR_LOGS_PATH, "error_logs.txt")

    # Read the JSONL files line by line
    for input_file in input_files:
        print(f"Processing {input_file}")

        with open(os.path.join(paths.BILL_SUM_PATH, input_file), "r") as infile:
            for line in infile:
                try:
                    data = process_json(line, "BILL")

                    reference_data = data.reference

                    summary_data = data.summary

                    write_to_file(reference_data, summary_data, "BILL_", data.id)

                    print(f"- Done - {data.title}")

                except Exception as e:
                    # Log the error to the error log file
                    with open(error_log_file, "a") as log_file:
                        log_file.write(f"Error processing {input_file}: {str(e)}\n")

    print("Extraction complete.")


def main():
    """Main Menu for testing purposes"""
    print("Choose an option:")
    print("1. Extract data from the bill summary dataset")
    print("2. Extract data from the government report dataset")
    choice = input("Enter your choice (1/2): ")
    if choice == "1":
        extract_bill_sum_dataset()
        # extract_dataset("BILL")
    elif choice == "2":
        extract_gov_report_dataset()
        # extract_dataset("GOVR")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
