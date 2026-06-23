"""
resume_parser.py — HireIQ
--------------------------
Extracts text from uploaded resume files.
Supports PDF and DOCX formats.
"""

import io
import os
import tempfile


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from a PDF file using pypdf."""
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
    pages_text = []

    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and text.strip():
            pages_text.append(f"[Page {page_num}]\n{text.strip()}")

    return "\n\n".join(pages_text)


def extract_text_from_docx(uploaded_file) -> str:
    """Extract all text from a DOCX file using python-docx."""
    import docx

    # python-docx needs a file path, so write to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        doc = docx.Document(tmp_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    finally:
        os.unlink(tmp_path)


def parse_resume(uploaded_file) -> str:
    """
    Parse a resume file and return extracted text.
    Supports PDF and DOCX.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type. Please upload a PDF or DOCX file.")
