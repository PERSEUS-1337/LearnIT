import os
import json
from rouge_score import rouge_scorer
from count_tokens import count_tokens_in_data, calculate_token_reduction
from utils import append_statistics_to_json, create_empty_file


def load_file_list(file_path):
    """Reads the file containing a list of files and returns it as a list."""
    with open(file_path, "r") as file:
        file_list = file.read().splitlines()
    print(f"> [READ] File list from {file_path} read...")
    return file_list


def load_json_file(folder_path, file_name):
    """Loads JSON data from the specified file in the given folder."""
    with open(os.path.join(folder_path, file_name), "r") as file:
        data = json.load(file)
    print(f"> [LOAD] Loaded JSON data from {file_name}...")
    return data["content"]


def calculate_rouge_scores(reference_data, generated_data):
    """Calculates ROUGE scores for reference and generated summaries."""
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL", "rougeLsum"], use_stemmer=True
    )
    scores = scorer.score(reference_data, generated_data)
    return scores


def process_files(reference_folder, generated_folder, file_list, output_file):
    """Processes files from the reference and generated folders."""
    for file_name in file_list:
        reference_file_path = os.path.join(reference_folder, file_name)
        generated_file_path = os.path.join(generated_folder, file_name)

        # Check if both files exist
        if os.path.exists(reference_file_path) and os.path.exists(generated_file_path):
            print(f"> [SUCCESS] {file_name} exists")
            # Load JSON data from reference and generated files
            reference_data = load_json_file(reference_folder, file_name)
            generated_data = load_json_file(generated_folder, file_name)
            ref_tokens = count_tokens_in_data(reference_data)
            gen_tokens = count_tokens_in_data(generated_data)
            reduction_percentage = calculate_token_reduction(ref_tokens, gen_tokens)

            # Calculate ROUGE scores
            rouge_scores = calculate_rouge_scores(reference_data, generated_data)

            # Print ROUGE scores
            print(f"\n\tROUGE Scores for file '{file_name}'\n")
            for metric, scores in rouge_scores.items():
                print(f"{metric}: {scores}")

            # Print Token Counts
            print(
                f"\tRef Tokens: {ref_tokens} | Gen'd Tokens: {gen_tokens} | Token Reduction: {reduction_percentage}\n"
            )

            # Append statistics to JSON file
            # output_json_file = "./rouge/1000_100.json"
            append_statistics_to_json(
                output_file,
                file_name,
                rouge_scores,
                ref_tokens,
                gen_tokens,
                reduction_percentage,
            )
        else:
            print(f"Files '{file_name}' not found in both directories.")


# Main function
def main():
    # Define paths
    reference_folder = "./extracted_data/references/"
    file_list_path = "./extracted_data/params_test.txt"
    chunk_size = int(input("Enter chunk size: "))
    chunk_overlap = int(input("Enter chunk overlap: "))
    generated_folder = f"./output_data/{chunk_size}_{chunk_overlap}"
    output_json_file = f"./rouge/{chunk_size}_{chunk_overlap}.jsonl"
    os.makedirs("./rouge", exist_ok=True)
    create_empty_file(output_json_file);

    # Read file list
    file_list = load_file_list(file_list_path)

    # Process files
    process_files(reference_folder, generated_folder, file_list, output_json_file)


if __name__ == "__main__":
    main()
