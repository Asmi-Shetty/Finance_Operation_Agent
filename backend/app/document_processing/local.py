import asyncio
from pathlib import Path
from pypdf import PdfReader
from app.document_processing.base import DocumentProcessor

class LocalDocumentProcessor(DocumentProcessor):
    async def extract_text(self,path: Path,media_type: str) -> str:
        if media_type=="application/pdf":
            return await asyncio.to_thread(lambda:"\n".join((p.extract_text() or "") for p in PdfReader(path).pages))
        return ""  # Image OCR is provided by a replaceable cloud/local adapter.

