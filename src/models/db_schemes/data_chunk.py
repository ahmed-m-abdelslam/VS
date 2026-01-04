from pydantic import BaseModel , Field , validator # type: ignore
from typing import List, Optional # type: ignore
from bson.objectid import ObjectId # type: ignore

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None,alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., getattr=0)
    chunk_project_id: ObjectId
    

    class Config:
        arbitrary_types_allowed = True