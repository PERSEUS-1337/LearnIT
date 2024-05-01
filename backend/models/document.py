from datetime import datetime
from typing import List
from pydantic import BaseModel


class UploadDoc(BaseModel):
    name: str
    uid: str
    uploaded_at: datetime

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        
class TSCC(BaseModel):
    uid: str
    processed: datetime
    chunks: List[str]
    
    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}
