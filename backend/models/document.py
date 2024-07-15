from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class Status(BaseModel):
    code: int
    message: str
    progress: Optional[int] = 0


class DocTokens(BaseModel):
    processed: datetime
    doc_loader_used: str
    token_count: int
    chunk_count: int
    chunks: List[dict]

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def details(self):
        return {
            "processed": self.processed.isoformat(),
            "doc_loader_used": self.doc_loader_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
        }

    def dict(self):
        return {
            "processed": self.processed.isoformat(),
            "doc_loader_used": self.doc_loader_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "chunks": self.chunks,
        }


class TSCC(BaseModel):
    processed: datetime
    process_time: float
    model_used: str
    token_count: int
    chunk_count: int
    chunks: List[str]

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def details(self):
        return {
            "processed": self.processed.isoformat(),
            "process_time": self.process_time,
            "model_used": self.model_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
        }

    def dict(self):
        return {
            "processed": self.processed.isoformat(),
            "process_time": self.process_time,
            "model_used": self.model_used,
            "token_count": self.token_count,
            "chunk_count": self.chunk_count,
            "chunks": self.chunks,
        }


class UploadDoc(BaseModel):
    oid: Optional[str] = None
    user_id: str  # Reference to the user's ID
    name: str
    file_uid: str
    uploaded_at: datetime
    vec_db_path: Optional[str] = None
    tokens: Optional[DocTokens] = None
    tscc: Optional[TSCC] = None
    tokenized: bool = False
    embedded: bool = False
    processed: bool = False
    status: Optional[Status] = None
    

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}

    def details(self):
        return {
            "name": self.name,
            "uploaded_at": self.uploaded_at.isoformat(),
            "tokenized": self.tokenized,
            "embedded": self.embedded,
            "processed": self.processed,
            "status": (
                self.status.model_dump() if self.status else None
            ),
        }
    
    def stat(self):
        return {
            "name": self.name,
            "uploaded_at": self.uploaded_at.isoformat(),
            "processed": self.processed,
            "status": (
                self.status.model_dump() if self.status else None
            ),
        }

    def dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "file_uid": self.file_uid,
            "uploaded_at": self.uploaded_at.isoformat(),
            "status": (
                self.status.model_dump() if self.status else None
            ),
            "tokenized": self.tokenized,
            "embedded": self.embedded,
            "processed": self.processed,
            "vec_db_path": self.vec_db_path,
            "tokens": self.tokens.model_dump() if self.tokens else None,
            "tscc": self.tscc.model_dump() if self.tscc else None,
        }
