# models.py
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, field_serializer, field_validator
from datetime import datetime
from bson import ObjectId

# ---------------- User Model ---------------- #
class UserModel(BaseModel):
    id: str = Field(..., alias="_id")
    email: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    role: str = "viewer"

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    # Convert ObjectId -> str automatically
    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @field_serializer("id")
    def serialize_id(self, v):
        return str(v)

# ---------------- Response Models ---------------- #
class DocumentResponse(BaseModel):
    status: str
    document_id: str
    message: Optional[str] = None

class AnalysisResponse(BaseModel):
    document_id: str
    user_id: str
    query: str
    status: str
    local_summary: Optional[Dict[str, Any]] = None
    crew_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
