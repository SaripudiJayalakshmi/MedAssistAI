# pdf_processor.py
# Handles extracting and chunking text from uploaded PDF files.

from pypdf import PdfReader  # library that reads PDF file contents
import re                    # Python's built-in regex module, used for cleaning text


def extract_text_from_pdf(file_path: str) -> str:
    """
    Opens a PDF file and pulls out all the raw text, page by page.
    Returns one big string with all pages concatenated.
    """
    reader = PdfReader(file_path)   # loads the PDF
    full_text = ""

    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()  # pulls text from a single page
        if page_text:                    # some pages might be empty/scanned images
            full_text += page_text + "\n"

    return full_text


def clean_text(raw_text: str) -> str:
    """
    Removes extra whitespace, weird line breaks, and other noise
    that PDFs commonly introduce when text is extracted.
    """
    # Replace multiple newlines/spaces with a single space
    cleaned = re.sub(r"\s+", " ", raw_text)
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    return cleaned


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """
    Splits a long string of text into overlapping chunks.

    chunk_size = how many characters per chunk
    overlap    = how many characters repeat between consecutive chunks,
                 so we don't lose context at the boundaries
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move the window forward, but step back by 'overlap' so chunks share some text
        start += chunk_size - overlap

    return chunks


def process_pdf(file_path: str) -> list[str]:
    """
    Full pipeline: extract -> clean -> chunk.
    This is the single function our API route will call.
    """
    raw_text = extract_text_from_pdf(file_path)
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned)
    return chunks