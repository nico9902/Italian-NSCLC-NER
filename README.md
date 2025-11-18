# Italian-NSCLC-NER  
**Named Entity Recognition in Italian clinical reports of Non-Small Cell Lung Cancer (NSCLC) using transformer models**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Paper](https://img.shields.io/badge/Paper-IEEE%202023-blue)](https://doi.org/10.1109/BIBM58861.2023.10385778)

Official repository of:  
**"Named Entity Recognition in Italian Lung Cancer Clinical Reports using Transformers"**  
*Domenico Paolo et al., IEEE BIBM 2023*

---

## Abstract
This repository provides the first publicly available transformer-based NER system designed specifically for **Italian clinical reports** of patients with **Non-Small Cell Lung Cancer (NSCLC)**.  
The model, fine-tuned from **MedBITR3+** (Biomedical BERT for Italian), achieves an average **F1-score of 84.3%** (strict entity-level) on **25 clinically relevant entity types**.

---

## Key Contributions
- Annotation of **758 real-world oncology and radiotherapy reports** (257 patients)  
- Definition of **25 NSCLC-specific entity types**  
- Custom preprocessing pipeline for Italian clinical text  
- Fine-tuning with **focal loss** to mitigate severe class imbalance  
- **10-fold patient-level cross-validation**  
- Outperforms mBERT and umBERTo by **>2.5% average F1**

---

## Entity Types
Full descriptions and examples are available in the guidelines:  
📄 [`annotation_guidelines.pdf`](annotation_guidelines.pdf)

| Acronym | Entity Type          | Example                                   |
|---------|---------------------|-------------------------------------------|
| CAN     | Cancer              | adenocarcinoma, bone metastasis           |
| COM     | Comorbidity         | COPD, type 2 diabetes                     |
| STA     | Cancer stage        | stage IV, advanced disease                |
| FAN     | Focal anomaly       | spiculated nodule, suspicious lesion      |
| POS     | Anatomical position | right upper lobe, left hilum              |
| TPY     | Therapy             | immunotherapy, radiotherapy               |
| DRU     | Drug                | pembrolizumab, osimertinib                |
| ...     | ...                 | ...                                       |

---

## Requirements
```bash
pip install -r requirements.txt`
```

## Data Preparation Pipeline

The full pipeline from raw PDF reports to training-ready folds:

```raw_pdf_reports/
└── *.pdf
    ↓
src/preprocessing/text_cleaning.py          ← Extracts only the narrative section (removes header, footer, and tables)
    ↓
clean_txt_reports/
└── *.txt
    ↓
Doccano<a href="https://doccano.github.io/doccano/" target="_blank" rel="noopener noreferrer nofollow"></a> ← Annotazione manuale seguendo annotation_guidelines.pdf
    ↓
doccano_export.jsonl
    ↓
src/preprocessing/doccano2json.py           ← Convert the JSONL file into standard JSON format
    ↓
data/processed/annotated_corpus.json
    ↓
src/preprocessing/group_k_fold.py           ← Create 10 folds by patient, ensuring that the same patient_id is always assigned to the same fold
    ↓
data/folds/
├── fold_0_train.json, fold_0_test.json
├── fold_1_train.json, fold_1_test.json
└── ... `
```

An example of a JSON file to provide as input to the NER model is available in data/data.json.

## Training & Evaluation

python run_ner.py \
    --model_name_or_path IVN-RIN/medBIT-r3-plus \
    --tokenizer_name IVN-RIN/medBIT-r3-plus \
    --train_file path/to/train.json \
    --validation_file path/to/valid.json \
    --test_file path/to/test.json \
    --output_dir outputs/exp1 \
    --num_train_epochs 12 \
    --per_device_train_batch_size 8 \
    --do_train True --do_eval True --do_predict True \
    --overwrite_output_dir True

## Results

Model,F1 (avg ± std),Precision,Recall
mBERT,81.7 ± 11.3,79.1,84.6
umBERTo,83.2 ± 9.0,80.0,86.7
MedBITR3+,84.3 ± 9.4,81.6,87.3
