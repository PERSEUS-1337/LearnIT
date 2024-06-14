from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class UploadDoc(BaseModel):
    name: str
    uid: str
    uploaded_at: datetime
    processed: bool = False  # Default since it is newly uploaded
    tscc_uid: Optional[str] = (
        None  # Reference to the TSCC document located in docs collection
    )

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class TSCC(BaseModel):
    uid: str
    processed: datetime
    model_used: str
    doc_loader_used: str
    chunk_size: int
    chunk_overlap: int
    token_count: int
    chunks_generated: int
    chunks: List[Dict[str, str]]

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def dict(self):
        return {
            "processed": self.processed.isoformat(),
            "model_used": self.model_used,
            "doc_loader_used": self.doc_loader_used,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "token_count": self.token_count,
            "chunks_generated": self.chunks_generated,
            "chunks": self.chunks,
        }

    def __str__(self) -> str:
        # Convert datetime to ISO format for readability
        processed_str = self.processed.isoformat()

        # Join chunks into a single string for display
        chunks_str = ", ".join(
            f"Prev: {chunk['prev']}, Curr: {chunk['curr']}" for chunk in self.chunks
        )

        return f"Processed: {processed_str}, Model Used: {self.model_used}, Doc Loader Used: {self.doc_loader_used},\nChunk Size: {self.chunk_size}, Chunk Overlap: {self.chunk_overlap}, Token Count: {self.token_count}, Chunks Generated: {self.chunks_generated}\nChunks: {chunks_str}"
