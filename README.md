# Italian-NSCLC-NER
**Named Entity Recognition in Italian clinical reports of Non-Small Cell Lung Cancer (NSCLC) using transformer models**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Paper](https://img.shields.io/badge/Paper-IEEE%202023-blue)](https://doi.org/10.1109/BIBM58861.2023.10385778)
[![arXiv](https://img.shields.io/badge/arXiv-2311.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXX.XXXXX)

Repository ufficiale del lavoro:  
**"Named Entity Recognition in Italian Lung Cancer Clinical Reports using Transformers"**  
Domenico Paolo et al., IEEE BIBM 2023

## Abstract
We present the first publicly available implementation of a transformer-based NER system specifically developed for Italian clinical notes of patients with Non-Small Cell Lung Cancer (NSCLC). The model, fine-tuned from **MedBITR3+** (Biomedical BERT for Italian), achieves an average **F1-score of 84.3%** (strict entity-level) on 25 clinically relevant entities.

## Key contributions
- Annotation of 758 real-world Italian oncology/radiotherapy reports (257 patients)
- Definition of **25 NSCLC-specific entity types**
- Custom preprocessing pipeline for Italian clinical text
- Fine-tuning with **focal loss** to handle severe class imbalance
- 10-fold patient-level cross-validation
- Outperforms mBERT and umBERTo by >2.5% F1 on average

## Entity types (25)
Full list with detailed descriptions and examples in:  
[annotation_guidelines.pdf](./docs/annotation_guidelines.pdf)

| Acronym | Entity                  | Example                              |
|---------|-------------------------|--------------------------------------|
| CAN     | Cancer                  | adenocarcinoma, metastasi ossea      |
| COM     | Comorbidity             | BPCO, diabete mellito tipo 2         |
| STA     | Cancer stage            | stadio IV, malattia avanzata         |
| FAN     | Focal anomaly           | nodulo spiculato, lesione sospetta  |
| POS     | Anatomical position     | lobo superiore destro, ilo sinistro |
| TPY     | Therapy                 | immunoterapia, radioterapia          |
| DRU     | Drug                    | pembrolizumab, osimertinib           |
| ...     | ...                     | ...                                  |

## Data Preparation Pipeline

The full pipeline from raw PDF reports to training-ready folds:

```text
raw_pdf_reports/
└── *.pdf
    ↓
src/preprocessing/text_cleaning.py          ← Estrae solo la parte narrativa (rimuove header, footer, tabelle)
    ↓
clean_txt_reports/
└── *.txt
    ↓
Doccano<a href="https://doccano.github.io/doccano/" target="_blank" rel="noopener noreferrer nofollow"></a> ← Annotazione manuale seguendo annotation_guidelines.pdf
    ↓
doccano_export.jsonl
    ↓
src/preprocessing/doccano2json.py           ← Converte JSONL → formato JSON standard
    ↓
data/processed/annotated_corpus.json
    ↓
src/preprocessing/group_k_fold.py           ← Crea 10 fold per paziente (stesso patient_id sempre nella stessa fold)
    ↓
data/folds/
├── fold_0_train.json, fold_0_test.json
├── fold_1_train.json, fold_1_test.json
└── ...

## Requirements 
pip install -r requirements.txt
