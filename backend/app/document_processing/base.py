from abc import ABC, abstractmethod
from pathlib import Path

class DocumentProcessor(ABC):
    @abstractmethod
    async def extract_text(self, path: Path, media_type: str) -> str: ...

