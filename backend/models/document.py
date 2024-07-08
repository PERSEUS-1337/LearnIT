from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class UploadDoc(BaseModel):
    uid: str
    name: str
    uploaded_at: datetime
    tokenized: bool = False
    embedded: bool = False
    processed: bool = False
    tokens_id: Optional[str] = None
    vec_db_path: Optional[str] = None
    tscc_id: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "uploaded_at": self.uploaded_at.isoformat(),
            "tokenized": self.tokenized,
            "embedded": self.embedded,
            "processed": self.processed,
            "tokens_id": self.tokens_id,
            "vec_db_path": self.vec_db_path,
            "tscc_id": self.tscc_id,
        }


class DocTokens(BaseModel):
    doc_uid: str
    processed: datetime
    doc_loader_used: str
    token_count: int
    chunk_count: int
    chunks: List[Dict[str, str]]

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def dict(self):
        return {
            "doc_uid": self.doc_uid,
            "processed": self.processed.isoformat(),
            "doc_loader_used": self.doc_loader_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "chunks": self.chunks,
        }

    def details(self):
        return {
            "doc_uid": self.doc_uid,
            "processed": self.processed.isoformat(),
            "doc_loader_used": self.doc_loader_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
        }


class TSCC(BaseModel):
    doc_uid: str
    processed: datetime
    process_time: float
    model_used: str
    token_count: int
    chunk_count: int
    chunks: List[str]

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def dict(self):
        return {
            "doc_uid": self.doc_uid,
            "processed": self.processed.isoformat(),
            "process_time": self.process_time,
            "model_used": self.model_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "chunks": self.chunks,
        }

    def details(self):
        return {
            "doc_uid": self.doc_uid,
            "processed": self.processed.isoformat(),
            "process_time": self.process_time,
            "model_used": self.model_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
        }
