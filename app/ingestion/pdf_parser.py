import pdfplumber
from pathlib import Path
from app.ingestion.cleaner import clean_extracted_text

def parse_pdf(file_path: str) -> str:
    """Extracts and cleans raw text content from a given PDF file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found at path: {file_path}")

    extracted_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

    return clean_extracted_text(extracted_text)