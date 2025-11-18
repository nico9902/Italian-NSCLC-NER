"""
Clean clinical report TXT files by extracting only the narrative part.

Usage
  python3 src/preprocessing/text_cleaning.py \
    --input_dir /path/to/CLARO_txt \
    --output_dir /path/to/CLARO_clean

Notes
- Traverses subdirectories under `--input_dir` and writes cleaned files to the
  mirrored structure under `--output_dir`.
- Processes only files whose names include "prima visita" or "visita".
"""

# import required libraries
import re
import os
import argparse
from src.preprocessing.doccano_utils import text_pre

parser = argparse.ArgumentParser(description="Extract narrative text from clinical report TXT files")
parser.add_argument("--input_dir", "-i", required=True, help="Root directory containing the source TXT files")
parser.add_argument("--output_dir", "-o", required=True, help="Root directory to write the cleaned TXT files")
args = parser.parse_args()

# input/output roots
dataset = args.input_dir
new_dataset = args.output_dir

for subdir in os.listdir(dataset):
    subdir_path = os.path.join(dataset, subdir)
    new_subdir_path = os.path.join(new_dataset, subdir)

    if not os.path.isdir(subdir_path):
        continue
    
    for patient in os.listdir(subdir_path):
        patient_path = os.path.join(subdir_path, patient)
        new_patient_path = os.path.join(new_subdir_path, patient)

        if not os.path.isdir(patient_path):
            continue
        os.makedirs(new_patient_path, exist_ok=True)

        for filename in os.listdir(patient_path):
            file_path = os.path.join(patient_path, filename)
            new_file_path = os.path.join(new_patient_path, filename)

            if "prima visita" not in filename.lower() and "visita" not in filename.lower():
                continue
            
            # reading txt file of the clinical report
            with open(file_path, 'r', encoding="utf-8") as f:
                text = f.read()

            # text pre-processing
            # deleting non-relevant expression
            # extracting only narrative part
            narrativa, _ = text_pre(text) 

            if narrativa is not None:
                # Deleting last page informations
                pattern = re.compile(r'\n\n\nFirma.*?\n\n', re.DOTALL)
                narrativa = re.sub(pattern, '', narrativa)

                # Deleting last part of clinical report
                pattern = re.compile(r'\n\n(Il medico responsabile|grading medico|Il radioterapista oncologo|medico:|Contatti:).*', re.DOTALL)
                narrativa = pattern.sub('', narrativa)

                # Deleting expressions across pages
                pattern = re.compile(r'Via alvaro del portillo.*?www\.policlinicocampusbiomedico\.it', re.DOTALL)
                narrativa = pattern.sub('', narrativa)
                
                # Save the obtained text in a new text file
                with open(new_file_path, 'w', encoding="utf-8") as f:
                    f.write(narrativa)
            


