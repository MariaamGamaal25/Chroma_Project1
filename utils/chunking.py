import re
import uuid
from typing import List, Dict

def chunk_by_headlines(text: str, filename: str) -> List[Dict]:
    """
    Splits text into chunks using headlines and returns them in the required format.
    If no headlines are found, it falls back to a paragraph-based chunking.

    Args:
        text (str): The full text content of the document.
        filename (str): The name of the original file for metadata.

    Returns:
        List[Dict]: A list of dictionaries, where each dict contains
                    {"id", "text", "metadata"}.
    """
    lines = text.splitlines()
    chunks = []
    current_headline = None
    buffer = []
    
    # This regex is a more robust way to find headlines
    # It looks for lines that are short, not just capitalized,
    # to better handle various document formats.
    headline_pattern = re.compile(r"^\s*([A-Z].*)\s*$", re.MULTILINE)

    # First, try to chunk by headlines
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if headline_pattern.match(line) and len(line.split()) < 10:
            if current_headline and buffer:
                chunk_text = "\n".join(buffer).strip()
                if chunk_text:
                    chunks.append({
                        "id": str(uuid.uuid4()),
                        "text": chunk_text,
                        "metadata": {
                            "filename": filename,
                            "section": current_headline
                        }
                    })
            current_headline = line
            buffer = []
        else:
            buffer.append(line)

    # Save last chunk
    if current_headline and buffer:
        chunk_text = "\n".join(buffer).strip()
        if chunk_text:
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "section": current_headline
                }
            })

    # If headline-based chunking yields no results, fall back to simple paragraph splitting
    if not chunks:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for i, paragraph in enumerate(paragraphs):
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": paragraph,
                "metadata": {
                    "filename": filename,
                    "section": f"Paragraph {i+1}"
                }
            })

    return chunks

# The chunk_with_subsections function from your file is not called in your current
# application logic, so it's not the source of this problem.
