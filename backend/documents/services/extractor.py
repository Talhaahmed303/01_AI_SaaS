import os
import hashlib
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """
    Extracts text and page-level metadata from PDF, DOCX, TXT, and Markdown files.
    """

    @staticmethod
    def calculate_sha256(file_obj) -> str:
        file_obj.seek(0)
        hasher = hashlib.sha256()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        file_obj.seek(0)
        return hasher.hexdigest()

    @staticmethod
    def extract(file_path: str, file_type: str) -> List[Tuple[int, str]]:
        """
        Returns a list of (page_number, text_content).
        For plain text/docx without strict pages, page_number is 1 or segmented logically.
        """
        file_type = file_type.lower()
        pages = []

        try:
            if file_type == 'pdf' or file_path.endswith('.pdf'):
                pages = DocumentExtractor._extract_pdf(file_path)
            elif file_type == 'docx' or file_path.endswith('.docx'):
                pages = DocumentExtractor._extract_docx(file_path)
            elif file_type in ['txt', 'md', 'markdown'] or file_path.endswith(('.txt', '.md')):
                pages = DocumentExtractor._extract_text(file_path)
            else:
                # Fallback to UTF-8 text read
                pages = DocumentExtractor._extract_text(file_path)
        except Exception as e:
            logger.error(f"Error extracting document {file_path}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to extract document contents: {str(e)}")

        return pages

    @staticmethod
    def _extract_pdf(file_path: str) -> List[Tuple[int, str]]:
        pages = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text").strip()
                if text:
                    pages.append((page_num + 1, text))
            doc.close()
        except ImportError:
            # Fallback to pypdf
            import pypdf
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ''
                    if text.strip():
                        pages.append((i + 1, text.strip()))
        return pages

    @staticmethod
    def _extract_docx(file_path: str) -> List[Tuple[int, str]]:
        pages = []
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            pages.append((1, full_text))
        except Exception as e:
            logger.warning(f"DOCX extraction fallback: {e}")
            with open(file_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
                pages.append((1, content))
        return pages

    @staticmethod
    def _extract_text(file_path: str) -> List[Tuple[int, str]]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return [(1, content)]
