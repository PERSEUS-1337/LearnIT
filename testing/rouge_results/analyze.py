import json
import os

def analyze_data(json_file):
    avg_tokens_per_reference_total = 0
    avg_rouge_scores_total = {"rouge1": 0, "rouge2": 0, "rougeL": 0, "rougeLSum": 0}
    avg_token_reduction_percent_total = 0
    num_entries = 0

    with open(json_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            avg_tokens_per_reference_total += data["ref_tokens"]
            avg_rouge_scores_total["rouge1"] += data["rouge1_f1"]
            avg_rouge_scores_total["rouge2"] += data["rouge2_f1"]
            avg_rouge_scores_total["rougeL"] += data["rougeL_f1"]
            avg_rouge_scores_total["rougeLSum"] += data["rougeLsum_f1"]
            avg_token_reduction_percent_total += data["reduction_percentage"]
            num_entries += 1

    avg_tokens_per_reference = avg_tokens_per_reference_total / num_entries

    avg_rouge_scores = {metric: score / num_entries for metric, score in avg_rouge_scores_total.items()}

    avg_token_reduction_percent = avg_token_reduction_percent_total / num_entries

    return avg_tokens_per_reference, avg_rouge_scores, avg_token_reduction_percent

def main():
    json_files = [file for file in os.listdir('./reformatted') if file.endswith('.jsonl')]
    highest_avg_rouge_scores = {"rouge1": -1, "rouge2": -1, "rougeL": -1, "rougeLSum": -1}
    highest_avg_token_reduction_percent = -1
    files_with_highest_rouge = {"rouge1": None, "rouge2": None, "rougeL": None, "rougeLSum": None}
    file_with_highest_token_reduction_percent = None

    results = []

    with open('results.txt', 'w') as output_file:
        for json_file in json_files:
            avg_tokens_per_reference, avg_rouge_scores, avg_token_reduction_percent = analyze_data(json_file)
            output_file.write(f"File: {json_file}\n")
            output_file.write(f"Avg Tokens Per Reference: {avg_tokens_per_reference}\n")
            output_file.write("Avg Rouge Scores:\n")
            for metric, score in avg_rouge_scores.items():
                output_file.write(f"\t{metric}: {score}\n")
                # Check if this file has the highest average ROUGE score for this metric
                if score > highest_avg_rouge_scores[metric]:
                    highest_avg_rouge_scores[metric] = score
                    files_with_highest_rouge[metric] = json_file
            output_file.write(f"Avg Token Reduction Percent: {avg_token_reduction_percent}\n")
            # Check if this file has the highest average token reduction percentage
            if avg_token_reduction_percent > highest_avg_token_reduction_percent:
                highest_avg_token_reduction_percent = avg_token_reduction_percent
                file_with_highest_token_reduction_percent = json_file
            output_file.write("\n")

            # Append results to list for JSON output
            results.append({
                "File": json_file,
                "Avg Tokens Per Reference": avg_tokens_per_reference,
                "Avg Rouge Scores": avg_rouge_scores,
                "Avg Token Reduction Percent": avg_token_reduction_percent
            })

        # Write the files with the highest average ROUGE scores to the output file
        output_file.write("\nFiles with Highest Avg ROUGE Scores:\n")
        for metric, file_with_highest_rouge in files_with_highest_rouge.items():
            output_file.write(f"{metric}: {file_with_highest_rouge}\n")

        # Write the file with the highest average token reduction percentage to the output file
        output_file.write(f"\nFile with Highest Avg Token Reduction Percentage: {file_with_highest_token_reduction_percent}\n")

    # Write results to JSON file
    with open('results.json', 'w') as json_output_file:
        json.dump(results, json_output_file, indent=4)

if __name__ == "__main__":
    main()
