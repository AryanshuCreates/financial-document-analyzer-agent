# tools.py
import os
import re
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

from crewai.tools import BaseTool

# ---------------- PDF Tool Class ---------------- #
class ReadFinancialDocumentTool(BaseTool):
    name: str = "read_financial_document"
    description: str = "Reads and extracts text from a PDF financial document."

    async def _run(self, path: str) -> str:
        if not isinstance(path, (str, Path)):
            raise ValueError("Path must be a string or Path object")
        path = str(path)
        text = await self.extract_text_from_pdf(path)
        if len(text.strip()) < 100:  # fallback to OCR
            ocr_text = await self.ocr_pdf(path)
            if len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        return text

    async def extract_text_from_pdf(self, path: str) -> str:
        from pypdf import PdfReader

        def _extract():
            reader = PdfReader(path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)

        return re.sub(r'\s+', ' ', await asyncio.to_thread(_extract)).strip()

    async def ocr_pdf(self, path: str) -> str:
        try:
            from pdf2image import convert_from_path
            import pytesseract

            def _ocr():
                text_parts = []
                pages = convert_from_path(path, dpi=200, fmt="jpeg")
                for page in pages:
                    page_text = pytesseract.image_to_string(page, config='--psm 6')
                    if page_text.strip():
                        text_parts.append(page_text)
                return "\n".join(text_parts)

            return re.sub(r'\s+', ' ', await asyncio.to_thread(_ocr)).strip()
        except ImportError:
            logger.warning("OCR dependencies not installed. Install pdf2image and pytesseract for OCR support.")
            return ""

# ---------------- Wrapper Functions ---------------- #
async def read_financial_document(path: str) -> str:
    """Standalone function for text extraction from PDF."""
    tool = ReadFinancialDocumentTool()
    return await tool._run(path)

async def analyze_investment_text(text: str) -> dict:
    """Basic financial text analysis without CrewAI dependencies."""
    if not text or not text.strip():
        return {"error": "No text to analyze"}

    word_count = len(text.split())
    financial_keywords = [
        'revenue', 'profit', 'loss', 'assets', 'liabilities', 'equity',
        'cash flow', 'dividend', 'earnings', 'investment', 'risk',
        'market', 'growth', 'volatility', 'returns'
    ]
    found_keywords = [kw for kw in financial_keywords if kw.lower() in text.lower()]

    return {
        "summary": text[:500] + "..." if len(text) > 500 else text,
        "word_count": word_count,
        "financial_keywords_found": found_keywords,
        "confidence": min(len(found_keywords) / len(financial_keywords), 1.0),
        "analysis_type": "basic_text_analysis"
    }
