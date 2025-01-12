from typing import List

from ..config import CHUNK_OVERLAP, CHUNK_SIZE
from ..model import Chunk, File
from .base_chunker import Chunker


class SizeChunker(Chunker):
    """Chunker that splits text based on character size."""

    def __init__(self, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

        # Validate inputs
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

    def chunk_text(self, file: File) -> List[Chunk]:
        """Split text into overlapping chunks based on character size.

        Args:
            file: File to split

        Returns:
            List[Chunk]: List of text chunks
        """
        content = file.content or ""
        # If content is empty or effectively empty, return early
        if not content.strip():
            return []

        chunks = []
        start = 0
        chunk_index = 0

        # Optional: Define a max chunk limit if desired
        # max_chunks = 10_000  # adjust if needed

        while start < len(content):
            end = min(start + self.chunk_size, len(content))

            # Attempt to find a space near the end to split more cleanly
            if end < len(content):
                last_space = content.rfind(" ", start, end)
                if last_space != -1 and last_space > start:
                    end = last_space

            chunk_content = content[start:end].rstrip("\n\r")
            chunks.append(
                Chunk(
                    target_size=self.chunk_size,
                    content=chunk_content,
                    index=chunk_index,
                )
            )

            # If we've reached or surpassed the end, no more chunks needed
            if end >= len(content):
                break

            # Prepare next start position, accounting for overlap
            new_start = end - self.overlap

            # Guardrail: if we're not making forward progress, break
            if new_start <= start:
                break

            start = new_start
            chunk_index += 1

            # Optional additional safeguard:
            # if len(chunks) >= max_chunks:
            #     break

        return chunks
