# Another script to convert PDF to Markdown, using the marker library which is designed for this purpose. This should give better results than the fitz-based approach, as it is specifically built for converting PDFs to structured Markdown.
# Tested with my ruleset, but it kept crashing on the full OGL PDF
# Source: Github Repo - https://github.com/datalab-to/marker

import pathlib
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

pdf_path = "D&D_5e_OGL.pdf"
md_path = "data/D&D_5e_OGL_marker.md"

print("Loading models...")
model_dict = create_model_dict()

print("Converting PDF to Markdown...")
converter = PdfConverter(artifact_dict=model_dict)
rendered = converter(pdf_path)

markdown_text = rendered.markdown

pathlib.Path("data").mkdir(exist_ok=True)
pathlib.Path(md_path).write_text(markdown_text, encoding="utf-8")

print(f"Extracted text from {pdf_path} and saved to {md_path}")