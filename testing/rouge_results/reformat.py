import json

# Input and output file paths
file_name = "1250_200.json"
input_file_path = f"params_testing/{file_name}"
output_file_path = f"reformatted/{file_name}"

# Function to extract relevant data from each line
def process_line(line):
    data = json.loads(line)
    title = data["title"]
    rouge_scores = data["rouge_scores"]
    rouge1_f1 = rouge_scores["rouge1"][-1]
    rouge2_f1 = rouge_scores["rouge2"][-1]
    rougeL_f1 = rouge_scores["rougeL"][-1]
    rougeLsum_f1 = rouge_scores["rougeLsum"][-1]
    ref_tokens = data["ref_tokens"]
    gen_tokens = data["gen_tokens"]
    reduction_percentage = data["reduction_percentage"]
    
    print(f"> [PROCESS] {title}")
    return {
        "title": title,
        "rouge1_f1": rouge1_f1,
        "rouge2_f1": rouge2_f1,
        "rougeL_f1": rougeL_f1,
        "rougeLsum_f1": rougeLsum_f1,
        "ref_tokens": ref_tokens,
        "gen_tokens": gen_tokens,
        "reduction_percentage": reduction_percentage,
    }

# Process each line in the input file and write to output file
with open(input_file_path, "r") as infile, open(output_file_path, "w") as outfile:
    for line in infile:
        
        processed_data = process_line(line)
        json.dump(processed_data, outfile)
        outfile.write("\n")
