"""
Generate group k-fold splits from a JSONL NER dataset.
Groups are patient ids, ensuring sentences from the same patient appear
in only one fold.

Usage
    python3 src/preprocessing/group_k_fold.py \
        --input_file ./doccano/json/doccano_processed.json \
        --output_dir ./k_fold \
        --n_splits 10
"""

# import required libraries
import numpy as np
import json
import os
import argparse
from sklearn.model_selection import GroupKFold
from sklearn.utils import shuffle

parser = argparse.ArgumentParser(description="Group K-Fold split generator for NER JSONL dataset")
parser.add_argument("--input_file", "-i", default="./doccano/json/doccano_processed.json", help="Path to input JSONL dataset")
parser.add_argument("--output_dir", "-o", required=True, help="Directory to write k-fold splits into")
parser.add_argument("--n_splits", "-k", type=int, default=10, help="Number of folds (k)")
args = parser.parse_args()

# Read json lines dataset
with open(args.input_file, 'r', encoding="utf-8") as json_file:
    json_list = list(json_file)

# collecting patient ids, report ids, tokens, tags
ids = []
reports = []
tokens = []
tags = []
for json_idx, json_str in enumerate(json_list):
    ehr = json.loads(json_str)
    ids.append(ehr['id'])
    # reports.append(ehr['report_id'])
    tokens.append(ehr["tokens"])
    tags.append(ehr["ner_tags"])

ids = np.array(ids, dtype="object")
# reports = np.array(reports, dtype="object")
tokens = np.array(tokens, dtype='object')
tags = np.array(tags, dtype='object')

# k-fold
group_kfold = GroupKFold(n_splits=args.n_splits)
group_kfold.get_n_splits(tokens, tags, ids)

# data shuffle (optional)
# tokens, tags, ids = shuffle(tokens, tags, ids, random_state=0)

# Ensure output base directory exists
os.makedirs(args.output_dir, exist_ok=True)

for i, (train_index, test_index) in enumerate(group_kfold.split(tokens, tags, ids)):
    fold_dir = os.path.join(args.output_dir, f"exp_{i+1}th")
    os.makedirs(fold_dir, exist_ok=True)

    train_path = os.path.join(fold_dir, f"train_{i+1}.json")
    test_path = os.path.join(fold_dir, f"test_{i+1}.json")

    with open(train_path, 'w', encoding="utf-8") as f:
        for id, sentence_tokens, sentence_tags in zip(ids[train_index], tokens[train_index], tags[train_index]):
            data = {"id": id, "tokens": sentence_tokens, "ner_tags": sentence_tags}
            f.write(json.dumps(data, ensure_ascii=False))
            f.write('\n')

    with open(test_path, 'w', encoding="utf-8") as f:
        for id, sentence_tokens, sentence_tags in zip(ids[test_index], tokens[test_index], tags[test_index]):
            data = {"id": id, "tokens": sentence_tokens, "ner_tags": sentence_tags}
            f.write(json.dumps(data, ensure_ascii=False))
            f.write('\n')
