"""
Convert a directory tree of PDF clinical reports to TXT files.

Usage
    python3 src/preprocessing/pdf2txt.py \
        --input_dir /path/to/reports_pdf \
        --output_dir /path/to/reports_txt

Notes
- Recurses through subdirectories under `--input_dir` and mirrors the same
    structure under `--output_dir`.
- Skips PDFs whose filenames contain the substring "laborator" (to avoid
    lab/tabular reports), preserving the original behavior.
- Requires pdfminer.six.
    Install: pip install pdfminer.six
"""

# import required libraries
import os
import io
import argparse
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

# let define a function to convert pdf content in a textual string
def convert_pdf_to_string(file_path):
    output_string = StringIO()
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    
    return(output_string.getvalue())

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert PDFs to TXT, preserving directory structure")
    parser.add_argument("--input_dir", "-i", required=True, help="Root directory containing PDF files")
    parser.add_argument("--output_dir", "-o", required=True, help="Root directory to write TXT files")
    args = parser.parse_args()

    rootdir = args.input_dir
    rootdir_txt = args.output_dir

    # Walk input tree; write TXT files mirroring relative subdirectories
    for subdir, dirs, files in os.walk(rootdir):
        for file_pdf in files:
            # process only .pdf files (case-insensitive)
            if file_pdf.lower().endswith('.pdf'):
                filepath = os.path.join(subdir, file_pdf)
                rel_path = os.path.relpath(subdir, rootdir)  # relative subdir under input root
                base_name = os.path.splitext(os.path.basename(filepath))[0]

                # Skip laboratory/tabular PDFs
                if "laborator" in file_pdf.lower():
                    continue

                # Extract text with pdfminer
                text = convert_pdf_to_string(filepath)

                # Ensure output directory exists and write TXT
                out_dir = os.path.join(rootdir_txt, rel_path)
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, base_name + ".txt")
                with io.open(out_path, "w", newline='', encoding="utf-8") as filename_txt:
                    filename_txt.write(text)
                # else:
                #     # open the PDF file
                #     with open(filepath, 'rb') as f:
                #         # create a PDF object
                #         pdf = PyPDF2.PdfFileReader(f)
    
                #         # extract the text from the PDF
                #         text = ""
                #         for page in range(pdf.getNumPages()):
                #             text += pdf.getPage(page).extractText()

                #         with io.open(rootdir_txt + "\\" + p + "\\" + file_pdf[:-4] + ".txt", "w", newline='', encoding="utf-8") as filename_txt:
                #             filename_txt.write(text)
