from app.core.config import settings
from typing import List

class ChunkingService:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= text_len:
                break
            # Move forward by chunk_size - chunk_overlap
            advance = self.chunk_size - self.chunk_overlap
            if advance <= 0:
                advance = 1 # Prevent infinite loop
            start += advance
            
        return chunks
