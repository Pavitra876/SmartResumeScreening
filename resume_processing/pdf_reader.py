"""
resume_processing/pdf_reader.py
Extracts plain text from an uploaded PDF resume using pypdf.
"""

from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Takes a file-like object (e.g. from st.file_uploader) and returns
    all the text found inside it as a single string.

    Streamlit's file_uploader gives us an in-memory file object,
    so we pass it directly to PdfReader -- no need to save to disk first.
    """
    reader = PdfReader(uploaded_file)

    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"

    return full_text.strip()


def get_basic_stats(text: str) -> dict:
    """Quick sanity-check stats about the extracted text,
    useful for showing the user something happened."""
    return {
        "character_count": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
    }