import re

def clean_extracted_text(text: str) -> str:
    """Cleans extracted raw text from PDF documents."""
    if not text:
        return ""
    
    # Remove excessive blank lines and spaces
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Trim leading/trailing whitespace
    return text.strip()