# Another script to convert PDF to Markdown, using the pymupdf4llm library which is designed for better formatting and structure in the output Markdown.
# Doesn't have a GPU requirement, but should give better results than the fitz-based approach, as it is specifically built for converting PDFs to structured Markdown.
# Source: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html

import pathlib
from pathlib import Path
import pymupdf4llm

pdf_path = "D&D_5e_OGL.pdf"
md_path = "data/D&D_5e_OGL_1.md"

markdown = pymupdf4llm.to_markdown(pdf_path)

pathlib.Path("data").mkdir(exist_ok=True)
pathlib.Path(md_path).write_text(markdown, encoding="utf-8")
print(f"Converted {pdf_path} to Markdown and saved to {md_path}")