from pypdf import PdfReader
from docx import Document as DocxDocument
from sentence_transformers import SentenceTransformer
from typing import List

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text content from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extracts text content from a DOCX file."""
    doc = DocxDocument(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Splits a long text into smaller chunks."""
    # This is a simple splitter, for more advanced cases consider langchain's RecursiveCharacterTextSplitter
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]
