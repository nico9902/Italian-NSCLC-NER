# Italian-NSCLC-NER
**Named Entity Recognition in Italian clinical reports of Non-Small Cell Lung Cancer (NSCLC) using transformer models**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/paper-IEEE%202023-blue)](https://doi.org/10.1109/BIBM58861.2023.10385778)

Repository ufficiale del lavoro:  
**"Named Entity Recognition in Italian Lung Cancer Clinical Reports using Transformers"**  
Domenico Paolo et al., 2023  

## Abstract
We present the first publicly available implementation of a transformer-based NER system specifically developed for Italian clinical notes of patients with Non-Small Cell Lung Cancer (NSCLC). The model, fine-tuned from **MedBITR3+** (Biomedical BERT for Italian), achieves an average **F1-score of 84.3%** (strict entity-level) on 25 clinically relevant entities.

## Key contributions
- Annotation of 758 real-world Italian oncology/radiotherapy reports (257 patients)
- Definition of **25 NSCLC-specific entity types** (see table below)
- Custom Italian clinical sentence splitter & tokenizer
- Fine-tuning with **focal loss** to handle severe class imbalance
- 10-fold cross-validation (patient-level split)
- Comparison with mBERT and umBERTo (MedBITR3+ outperforms both)

## Entity types (25)

| Acronym | Entity               | Example                              |
|---------|----------------------|--------------------------------------|
| CAN     | Cancer               | adenocarcinoma, metastasi ossea      |
| COM     | Comorbidity          | diabete mellito tipo 2               |
| STA     | Cancer stage         | stadio IV, malattia avanzata         |
| FAN     | Focal anomaly        | nodulo polmonare                    |
| POS     | Anatomical position  | lobo superiore destro               |
| ...     | ...                  | ...                                  |

Full list in `docs/annotation_guidelines.pdf`.

## Requirements
```bash
pip install -r requirements.txt
