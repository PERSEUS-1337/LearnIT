from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class Document(BaseModel):
    filename: str
    title: str
    date_uploaded: datetime
    chunks: List[str]
    tscc_chunks: Optional[List[str]] = None
