import os
import json

import paths
import params


# Create output directories if they don't exist
os.makedirs(paths.REFERENCES_PATH, exist_ok=True)
os.makedirs(paths.SUMMARIES_PATH, exist_ok=True)

def extract_bill_sum_dataset(input_files):

    # Read the JSONL files line by line
    for input_file in input_files:
        with open(os.path.join(paths.BILL_SUM_PATH, input_file), "r") as infile:
            for line in infile:
                data = json.loads(line)
                bill_id = data["bill_id"]
                title = data.get("title", "")  # Get the title or default to empty string
                text = data["text"]

                summary = data["summary"]
                print(f"Processing {input_file}: {title}")

                # Write data to reference JSON file
                reference_data = {"title": title, "content": text}
                with open(os.path.join(paths.REFERENCES_PATH, f"{bill_id}.json"), "w") as ref_file:
                    json.dump(reference_data, ref_file, indent=4)

                # Write data to summary JSON file
                summary_data = {"title": title, "content": summary}
                with open(os.path.join(paths.SUMMARIES_PATH, f"{bill_id}.json"), "w") as summary_file:
                    json.dump(summary_data, summary_file, indent=4)

    print("Extraction complete.")


if __name__ == "__main__":
    bill_sum_files = ["ca_test_data_final_OFFICIAL.jsonl", "us_test_data_final_OFFICIAL.jsonl", "us_train_data_final_OFFICIAL.jsonl"]
    extract_bill_sum_dataset(bill_sum_files)
