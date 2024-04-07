import os
import json
import sys

import paths
import params

# Create output directories if they don't exist
os.makedirs(paths.REFERENCES_PATH, exist_ok=True)
os.makedirs(paths.SUMMARIES_PATH, exist_ok=True)

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')


##### BILL SUM FUNCTIONS
def extract_bill_sum_dataset():
    input_files = ["ca_test_data_final_OFFICIAL.jsonl", "us_test_data_final_OFFICIAL.jsonl",
                   "us_train_data_final_OFFICIAL.jsonl"]
    
    # Read the JSONL files line by line
    for input_file in input_files:
        
        print(f"Processing {input_file}")
        
        with open(os.path.join(paths.BILL_SUM_PATH, input_file), "r") as infile:
            for line in infile:
                data = json.loads(line)
                bill_id = data["bill_id"]
                title = data.get("title", "")  # Get the title or default to empty string
                text = data["text"]
                summary = data["summary"]
                
                print(f"- Processing '{title}'... ", end="", flush=True)

                # Write data to reference JSON file
                reference_data = {"title": title, "content": text}
                # Write data to summary JSON file
                summary_data = {"title": title, "content": summary}
                
                reference_output_file = os.path.join(paths.REFERENCES_PATH, f"BILL_SUM_{bill_id}.json")
                summary_output_file = os.path.join(paths.SUMMARIES_PATH, f"BILL_SUM_{bill_id}.json")
                
                with open(reference_output_file, "w") as ref_file:
                    json.dump(reference_data, ref_file, indent=4)

                with open(summary_output_file, "w") as summary_file:
                    json.dump(summary_data, summary_file, indent=4)
                    
                print(f"done", flush=True)
                    
    print("Extraction complete.")


##### GOV REPORT FUNCTIONS
def extract_summary(json_data):
    # Extract all summaries and combine them into a single string
    summaries = json_data["summary"]
    combined_summary = " ".join(summaries)
    return combined_summary


def extract_reference_text(json_data):
    # Extract reference text from paragraphs nested within the reports section
    paragraphs = []
    subsections = json_data["reports"]["subsections"]
    for subsection in subsections:
        paragraphs.extend(subsection["paragraphs"])
    reference_text = " ".join(paragraphs)
    return reference_text


def process_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        summary = extract_summary(json_data)
        reference_text = extract_reference_text(json_data)
        return summary, reference_text


def extract_gov_report_dataset():
    # Iterate over JSON files in the folder
    for file_name in os.listdir(paths.GOV_REPORT_PATH):
        if file_name.endswith(".json"):
            file_path = os.path.join(paths.GOV_REPORT_PATH, file_name)
            print(f"Processing {file_name}")
            summary, reference_text = process_json_file(file_path)
            # Write summary to summaries folder
            with open(os.path.join(paths.SUMMARIES_PATH, f"{file_name}"), "w") as summary_file:
                summary_file.write(summary)
            # Write reference text to references folder
            with open(os.path.join(paths.REFERENCES_PATH, f"{file_name}"), "w") as ref_file:
                ref_file.write(reference_text)


def main():
    print("Choose an option:")
    print("1. Extract data from the bill summary dataset")
    print("2. Extract data from the government report dataset")
    choice = input("Enter your choice (1/2): ")
    if choice == "1":
        extract_bill_sum_dataset()
    elif choice == "2":
        extract_gov_report_dataset()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
