from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class UploadDoc(BaseModel):
    uid: str
    name: str
    uploaded_at: datetime
    tokenized: bool = False
    processed: bool = False
    tokens_id: Optional[str] = None
    tscc_id: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "uploaded_at": self.uploaded_at.isoformat(),
            "tokenized": self.tokenized,
            "processed": self.processed,
            "tokens_id": self.tokens_id,
            "tscc_id": self.tscc_id,
        }


class DocTokens(BaseModel):
    processed: datetime
    doc_loader_used: str
    chunk_size: int
    chunk_overlap: int
    token_count: int
    chunk_count: int
    chunks: List[Dict[str, str]]

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def dict(self):
        return {
            "processed": self.processed.isoformat(),
            "doc_loader_used": self.doc_loader_used,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "chunks": self.chunks,
        }


class TSCC(BaseModel):
    processed: datetime
    model_used: str
    doc_loader_used: str
    chunk_size: int
    chunk_overlap: int
    token_count: int
    chunk_count: int
    chunks: List[str]

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
            "chunk_count": self.chunk_count,
            "chunks": self.chunks,
        }
