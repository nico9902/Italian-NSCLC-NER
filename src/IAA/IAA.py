import json
import math
import argparse

"""
Inter-Annotator Agreement (IAA) utilities for NER labels.

This script expects two line-delimited JSON files (A1, A2) with matching
documents. Each line represents one document as a JSON object containing
the sequence of tags under key "ner_tags". Example (one line):

{"ner_tags": ["B-PER", "I-PER", "O", ...]}

The script strips BIO prefixes to compare entity classes at token and entity-span
level and prints per-class precision/recall/F1 along with macro averages.

Usage:
  python3 src/IAA/IAA.py --a1 ./IAA/doccano_processed_a1.json --a2 ./IAA/doccano_processed_a2.json
"""

def calculate_std(numbers, mean):
    squared_diffs = [(x - mean) ** 2 for x in numbers]
    variance = sum(squared_diffs) / len(numbers)
    std_deviation = math.sqrt(variance)
    return std_deviation

def extract_entity_spans(entity_labels):
    """Return contiguous spans of the same non-'O' entity as (entity, start, end).

    entity_labels contains class names (BIO prefix removed) or 'O'.
    end is exclusive.
    """
    entity_spans = []
    current_entity = None
    start = None

    for i, label in enumerate(entity_labels):
        if label != 'O':
            if current_entity is None:
                current_entity = label
                start = i
            elif current_entity != label:
                entity_spans.append((current_entity, start, i))
                current_entity = label
                start = i
        elif current_entity is not None:
            entity_spans.append((current_entity, start, i))
            current_entity = None

    if current_entity is not None:
        entity_spans.append((current_entity, start, len(entity_labels)))

    return entity_spans

# annotation2 is the benchmark
def compute_token_iaa(annotation1, annotation2):
    """Token-level agreement: treat matching non-'O' tags as TP for that tag.

    annotation1 and annotation2 are flat lists of class names (no BIO) or 'O'.
    """
    tp_counts = {tag: 0 for tag in set(annotation1 + annotation2) if tag != 'O'}
    fp_counts = {tag: 0 for tag in set(annotation1 + annotation2) if tag != 'O'}
    fn_counts = {tag: 0 for tag in set(annotation1 + annotation2) if tag != 'O'}

    for ann1, ann2 in zip(annotation1, annotation2):
        if ann1 == ann2:
            if ann1 != 'O':
                tp_counts[ann1] += 1
        else:   
            if ann1 != 'O':
                fp_counts[ann1] += 1
            if ann2 != 'O':
                fn_counts[ann2] += 1

    precision = {}
    recall = {}
    f1 = {}
    for tag in tp_counts.keys():
        p_den = (tp_counts[tag] + fp_counts[tag])
        r_den = (tp_counts[tag] + fn_counts[tag])
        precision[tag] = tp_counts[tag] / p_den if p_den else 0.0
        recall[tag] = tp_counts[tag] / r_den if r_den else 0.0
        pr_sum = (precision[tag] + recall[tag])
        f1[tag] = 2 * (precision[tag] * recall[tag]) / pr_sum if pr_sum else 0.0

    average_f1 = (sum(f1.values()) / len(f1)) if f1 else 0.0
    std_f1 = calculate_std(list(f1.values()), average_f1) if f1 else 0.0

    return precision, recall, f1, average_f1, std_f1

# annotation2 is the benchmark
def compute_entity_iaa(annotation1, annotation2):
    """Entity-span agreement: compare contiguous spans of identical entity class.

    Spans must match exactly in class and boundaries.
    """
    tp_counts = {tag: 0 for tag in set(annotation1 + annotation2) if tag != 'O'}
    fp_counts = {tag: 0 for tag in set(annotation1 + annotation2) if tag != 'O'}
    fn_counts = {tag: 0 for tag in set(annotation1 + annotation2) if tag != 'O'}

    spans1 = extract_entity_spans(annotation1)
    spans2 = extract_entity_spans(annotation2)
    for span in spans2:
        entity,_,_ = span
        if span in spans1:
            tp_counts[entity] += 1   
        else:
            fn_counts[entity] += 1
    
    for span in spans1:
        entity,_,_ = span
        if span not in spans2:
            fp_counts[entity] += 1

    precision = {}
    recall = {}
    f1 = {}
    for tag in tp_counts.keys():
        p_den = (tp_counts[tag] + fp_counts[tag])
        r_den = (tp_counts[tag] + fn_counts[tag])
        precision[tag] = tp_counts[tag] / p_den if p_den else 0.0
        recall[tag] = tp_counts[tag] / r_den if r_den else 0.0
        pr_sum = (precision[tag] + recall[tag])
        f1[tag] = 2 * (precision[tag] * recall[tag]) / pr_sum if pr_sum else 0.0

    average_f1 = (sum(f1.values()) / len(f1)) if f1 else 0.0
    std_f1 = calculate_std(list(f1.values()), average_f1) if f1 else 0.0
    return precision, recall, f1, average_f1, std_f1

if __name__ == "__main__":
    # Parse CLI arguments for the two annotator files.
    parser = argparse.ArgumentParser(description="Compute Inter-Annotator Agreement (token/entity)")
    parser.add_argument("--a1", required=True, help="Path to annotator 1 line-delimited JSON file")
    parser.add_argument("--a2", required=True, help="Path to annotator 2 line-delimited JSON file")
    args = parser.parse_args()

    entity_labels_annotator1 = []
    entity_labels_annotator2 = []

    # Read files line-by-line to avoid loading entire datasets in memory.
    with open(args.a1, 'r', encoding="utf-8") as a1, open(args.a2, 'r', encoding="utf-8") as a2:
        json_list_a1 = list(a1)
        json_list_a2 = list(a2)
        for json_str_a1, json_str_a2 in zip(json_list_a1, json_list_a2):
            ehr_a1 = json.loads(json_str_a1)
            ehr_a2 = json.loads(json_str_a2)

            a1_ner_tags = ehr_a1["ner_tags"]
            a2_ner_tags = ehr_a2["ner_tags"]

            # Strip BIO prefixes to compare only the entity class (e.g., "PER").
            for a1_ner_tag, a2_ner_tag in zip(a1_ner_tags, a2_ner_tags):
                if a1_ner_tag != 'O':
                    a1_ner_tag = a1_ner_tag[2:]
                else:
                    a1_ner_tag = a1_ner_tag 
                if a2_ner_tag != 'O':
                    a2_ner_tag = a2_ner_tag[2:]
                else:
                    a2_ner_tag = a2_ner_tag
                       
                entity_labels_annotator1.append(a1_ner_tag)
                entity_labels_annotator2.append(a2_ner_tag)

    # Compute token- and entity-level agreement metrics.
    t_precision, t_recall, t_f1, t_average_f1, t_std_f1 = compute_token_iaa(entity_labels_annotator1, entity_labels_annotator2)
    e_precision, e_recall, e_f1, e_average_f1, e_std_f1 = compute_entity_iaa(entity_labels_annotator1, entity_labels_annotator2)

    # Print metrics in a readable form.
    print("Token-level metrics")
    print("Precision:", t_precision)
    print("Recall:", t_recall)
    print("F1 score:", t_f1)
    print("Average f1 score:", t_average_f1)
    print("Std f1 score:", t_std_f1)

    print("Entity-level metrics")
    print("Precision:", e_precision)
    print("Recall:", e_recall)
    print("F1 score:", e_f1)
    print("Average f1 score:", e_average_f1)
    print("Std f1 score:", e_std_f1)
