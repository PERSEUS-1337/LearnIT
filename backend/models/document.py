from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Document(BaseModel):
    filename: str
    title: str
    date_uploaded: datetime
    chunks: List[str]
    tscc_chunks: Optional[List[str]] = None


class UploadDoc(BaseModel):
    name: str
    uid: str
    date_uploaded: datetime  # Reference to the user who uploaded the file
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
