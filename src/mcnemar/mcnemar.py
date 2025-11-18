"""
McNemar test between two NER systems' predictions.

This script compares two systems at the token level using a 2x2 contingency
table and runs McNemar's test to check if their accuracies differ
significantly on the same dataset.

Inputs are line-based files where each line is a whitespace-separated
sequence of BIO tags (e.g., "B-PER I-PER O B-LOC ...").
Sequences across files must be aligned by line index and token count.

Usage example:
  python3 src/mcnemar/mcnemar.py \
    --pred1 ./results/medBIT-r3-plus/predictions.txt \
    --pred2 ./results/mBERT/predictions.txt \
    --label_file ./results/medBIT-r3-plus/labels.txt
"""

from statsmodels.stats.contingency_tables import mcnemar
import argparse

def extract_predictions_labels(prediction_file, label_file):
    """Read predictions and labels from text files.

    Returns two lists of lists: tokens' tags per sequence.
    """
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

def merge_tags(tags):
    """Merge BIO tags into entity classes and 'O'.

    Consecutive B-/I- segments of the same entity are collapsed to a
    single class label (e.g., [B-PER, I-PER] -> [PER]). 'O' tokens are
    preserved as 'O'.
    """
    merged_tags = []
    current_entity = None

    for tag in tags:
        prefix = tag[0]
        entity = tag[2:]

        if prefix == "O":
            if current_entity:
                merged_tags.append(current_entity)
            merged_tags.append("O")
            current_entity = None

        if prefix == "B":
            if current_entity:
                merged_tags.append(current_entity)
            current_entity = entity 

        elif prefix == "I":
            if current_entity:
                if entity == current_entity:
                    continue
                else:
                    merged_tags.append(current_entity)
                    current_entity = entity

    if current_entity:
        merged_tags.append(current_entity)

    return merged_tags

if __name__ == "__main__":
    # Parse CLI arguments for two prediction files and labels file.
    parser = argparse.ArgumentParser(description="Run McNemar test for two NER systems")
    parser.add_argument("--pred1", required=True, help="Path to first predictions file (BIO tags)")
    parser.add_argument("--pred2", required=True, help="Path to second predictions file (BIO tags)")
    parser.add_argument(
        "--label_file",
        default="./results/dataset_257/medBIT-r3-plus/labels.txt",
        help="Path to gold labels file (BIO tags). Default keeps previous behavior.",
    )
    args = parser.parse_args()

    predictions1, labels = extract_predictions_labels(args.pred1, args.label_file)
    predictions2, labels = extract_predictions_labels(args.pred2, args.label_file)

    # Initialize the matrix
    matrix = [[0, 0], [0, 0]]
    # Check if the predictions are the same or different
    for seq_predictions1,seq_predictions2,seq_labels in zip(predictions1, predictions2, labels):
        # Collapse BIO sequences to entity-level and 'O'
        seq_predictions1 = merge_tags(seq_predictions1)
        seq_predictions2 = merge_tags(seq_predictions2)
        seq_labels = merge_tags(seq_labels)
        for prediction1,prediction2,label in zip(seq_predictions1,seq_predictions2,seq_labels):
            if prediction1==label and prediction2==label:
                if label != "O":
                    matrix[0][0] += 1  # Both classifiers correct
            elif prediction1==label and prediction2!=label:
                matrix[0][1] += 1  # Classifier 1 correct, but not classifier 2
            elif prediction2==label and prediction1!=label:
                matrix[1][0] += 1  # Classifier 2 correct, but not classifier 1
            else:
                matrix[1][1] += 1  # Both classifiers incorrect
    
    # Perform the McNemar test
    print(mcnemar(matrix, exact=False, correction=False))
