# Let's import the following libraries
"""
Compute NER performance metrics from saved predictions and labels.

Usage
- CLI (pass paths to text files):
    python3 src/compute_performances.py \
        --prediction_file ./predictions.txt \
        --label_file ./labels.txt

Inputs
- prediction_file: text file with one sequence per line; each line contains
    whitespace-separated label strings (e.g., BIO tags) predicted for tokens.
- label_file: text file with the same format and alignment as predictions,
    containing the gold label strings for the corresponding tokens.

Output
- metrics_dict.json: JSON containing per-entity metrics (precision, recall,
    f1, fbeta, number) and overall metrics (precision, recall, f1, accuracy,
    fbeta) plus means/std across entity f1/precision/recall.

Notes
- This script uses the `evaluate` package with the `seqeval` metric.
    Ensure dependencies are installed: pip install -r requirements.txt
"""
import json
import math
import evaluate
import argparse

# Metric
seqeval = evaluate.load('seqeval')

def calculate_std(numbers, mean):
    squared_diffs = [(x - mean) ** 2 for x in numbers]
    variance = sum(squared_diffs) / len(numbers)
    std_deviation = math.sqrt(variance)
    return std_deviation

def calculate_performance(predictions, labels):
    results = seqeval.compute(predictions=predictions, references=labels)#, mode='strict', scheme='IOB2')
    
    return results

def extract_predictions_labels(prediction_file, label_file):
    with open(prediction_file) as f:
        predictions = [str(x.strip()) for x in f.readlines()]
    true_predictions = []
    for prediction in predictions:
        true_predictions.append(prediction.split())

    with open(label_file) as f:
        labels = [str(x.strip()) for x in f.readlines()]
    true_labels = []
    for label in labels:
        true_labels.append(label.split())
    
    return true_predictions, true_labels

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute NER performance metrics using seqeval")
    parser.add_argument("--prediction_file", "-p", required=True, help="Path to predictions text file (one sequence per line)")
    parser.add_argument("--label_file", "-l", required=True, help="Path to labels text file (one sequence per line)")
    args = parser.parse_args()

    predictions, labels = extract_predictions_labels(args.prediction_file, args.label_file)
    
    results = calculate_performance(predictions, labels)
    beta = 2

    post_results = {}
    f1 = []
    p = []
    r = []
    for entity, measures in results.items():
        if entity != 'overall_precision' and entity != 'overall_recall' and entity != 'overall_f1' and entity != 'overall_accuracy': 
            post_results[entity] = {'precision': float(measures['precision']), 'recall': float(measures['recall']), 'f1': float(measures['f1']), 'fbeta': float((1+(beta*beta))*((measures['precision']*measures['recall'])/(((beta*beta)*measures['precision'])+measures['recall']))), 'number': int(measures['number'])}
            f1.append(measures['f1'])
            p.append(measures['precision'])
            r.append(measures['recall'])

    post_results['overall_precision'] = float(results['overall_precision'])
    post_results['overall_recall'] = float(results['overall_recall'])
    post_results['overall_f1'] = float(results['overall_f1'])
    post_results['overall_accuracy'] = float(results['overall_accuracy'])
    fbeta = (1+(beta*beta))*((results['overall_precision']*results['overall_recall'])/(((beta*beta)*results['overall_precision'])+results['overall_recall']))
    post_results['overall_fbeta'] = float(fbeta)
    post_results['mean_f1'] = float(sum(f1)/len(f1))
    post_results['std_f1'] = calculate_std(f1, post_results['mean_f1'])
    post_results['mean_precision'] = float(sum(p)/len(p))
    post_results['std_precision'] = calculate_std(p, post_results['mean_precision'])
    post_results['mean_recall'] = float(sum(r)/len(r))
    post_results['std_recall'] = calculate_std(r, post_results['mean_recall'])

    output_metrics_file = "metrics_dict.json"
    with open(output_metrics_file, 'w') as f:
        f.write(json.dumps(post_results, ensure_ascii=False, indent=4))
