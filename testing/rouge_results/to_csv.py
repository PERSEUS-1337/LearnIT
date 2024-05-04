import os
import json
import csv

def jsonl_to_csv(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through each .jsonl file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".jsonl"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, os.path.splitext(filename)[0] + ".csv")
            convert_file(input_file, output_file)
            print(f"Converted {input_file} to {output_file}")

def convert_file(input_file, output_file):
    print("ok")
    with open(input_file, 'r') as f:
        data = f.readlines()

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        header = ["title", "rouge1_f1", "rouge2_f1", "rougeL_f1", "rougeLsum_f1", "ref_tokens", "gen_tokens", "reduction_percentage"]
        writer.writerow(header)
        
        # Write data
        for line in data:
            record = json.loads(line.strip())
            writer.writerow([record.get(field, "") for field in header])

# Example usage
input_folder = "./reformatted"
output_folder = "./reformatted"
jsonl_to_csv(input_folder, output_folder)
