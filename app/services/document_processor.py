import asyncio
import io
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import PyPDF2
import pytesseract
import spacy
from PIL import Image
from docx import Document as DocxDocument
from google.cloud import translate_v2 as translate
import fitz  # PyMuPDF

# Stubs for libraries that might not be installed
try:
    import speech_recognition as sr
except ImportError:
    sr = None
try:
    import moviepy.editor as mp
except ImportError:
    mp = None


from app.models import Document, DocumentType
from app.services.ai_service import AIService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.ai_service = AIService()
        self.vector_service = VectorService()
        # self.translate_client = translate.Client() # This would require authentication

        try:
            self.nlp = spacy.load("pl_core_news_sm")
        except OSError:
            logger.warning("Polish spaCy model not found, downloading 'en_core_web_sm'. Run 'python -m spacy download pl_core_news_sm' for Polish.")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("Default spaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
                self.nlp = None

    async def _download_file(self, file_path: str) -> bytes:
        # This is a stub. In a real app, this would download from GCS, S3, etc.
        logger.warning(f"Using local file at '{file_path}' for processing. GCS download is stubbed.")
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return content
        except FileNotFoundError:
            logger.error(f"Local file not found at {file_path}. Returning empty content.")
            return b""


    async def extract_text(self, document: Document) -> str:
        """Extract text from various document types"""

        # In a real app, you'd pass the GCS path. For this stub, we assume a local path.
        # content = await self._download_file(document.file_path)
        # For now, let's create some dummy content based on type
        dummy_content = b"This is dummy content."

        if document.document_type == DocumentType.PDF:
            return await self._extract_from_pdf(dummy_content)
        elif document.document_type == DocumentType.DOCX:
            return await self._extract_from_docx(dummy_content)
        elif document.document_type == DocumentType.TXT:
            return dummy_content.decode('utf-8')
        elif document.document_type == DocumentType.AUDIO:
            return await self._transcribe_audio(dummy_content, document.content_type)
        elif document.document_type == DocumentType.VIDEO:
            return await self._transcribe_video(dummy_content)
        else:
            raise ValueError(f"Unsupported document type: {document.document_type}")

    async def _extract_from_pdf(self, content: bytes) -> str:
        text = ""
        try:
            pdf_file = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_file.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + "\n"

            if not text.strip():
                text = await self._ocr_pdf(content)

        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}, falling back to OCR.")
            text = await self._ocr_pdf(content)

        return text or "Dummy PDF text."

    async def _ocr_pdf(self, content: bytes) -> str:
        text = ""
        try:
            pdf_document = fitz.open(stream=content, filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                page_text = pytesseract.image_to_string(img, lang='pol+eng')
                text += page_text + "\n"
            pdf_document.close()
        except Exception as e:
            logger.error(f"OCR PDF processing failed: {e}")
            return "Dummy OCR text."
        return text

    async def _extract_from_docx(self, content: bytes) -> str:
        try:
            doc = DocxDocument(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs]) or "Dummy DOCX text."
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return "Dummy DOCX text."

    async def _transcribe_audio(self, content: bytes, content_type: str) -> str:
        if not sr:
            return "SpeechRecognition library not installed."
        # Placeholder
        return "Dummy transcribed audio."

    async def _transcribe_video(self, content: bytes) -> str:
        if not mp:
            return "MoviePy library not installed."
        # Placeholder
        return "Dummy transcribed video."

    async def detect_language(self, text: str) -> str:
        # Placeholder for language detection
        return "pl"

    async def classify_document(self, text: str) -> Dict[str, Any]:
        # Placeholder for classification
        return {
            'category': 'contract',
            'legal_areas': ['civil'],
            'jurisdiction': 'PL',
            'confidence': 0.9
        }

    async def create_chunks(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        if not text:
            return []
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]


    async def extract_legal_entities(self, text: str) -> Dict[str, Any]:
        if not self.nlp:
            return {}

        doc = self.nlp(text)
        entities = {'persons': [], 'organizations': [], 'locations': [], 'dates': []}
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(entities['persons']) < 50:
                entities['persons'].append(ent.text)
            elif ent.label_ == "ORG" and len(entities['organizations']) < 50:
                entities['organizations'].append(ent.text)
        return entities

    async def generate_summary(self, text: str) -> str:
        return await self.ai_service.generate_summary(text)

    async def generate_embeddings(self, document: Document, chunks: List[str]) -> str:
        return await self.vector_service.generate_embeddings(document, chunks)
