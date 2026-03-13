# Script to convert PDF to Markdown
# Converted PDF to Markdown, but the formatting is not great. This is a simple extraction of text from the PDF using fitz (PyMuPDF).

import pathlib
from pathlib import Path
import fitz

pdf_path = "D&D_5e_OGL.pdf"
md_path = "data/D&D_5e_OGL.md"

doc = fitz.open(pdf_path)
text = "\n\n".join(page.get_text() for page in doc)

pathlib.Path("data").mkdir(exist_ok=True)
pathlib.Path(md_path).write_text(text, encoding="utf-8")
print(f"Extracted {len(doc)} pages from {pdf_path} and saved to {md_path}")