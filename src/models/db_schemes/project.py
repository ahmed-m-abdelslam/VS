from pydantic import BaseModel , Field , validator # type: ignore
from typing import List, Optional # type: ignore
from bson.objectid import ObjectId # type: ignore

class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1)


    @validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("Project ID cannot be empty")
        return value
    
    class Config:
        arbitrary_types_allowed = True
        