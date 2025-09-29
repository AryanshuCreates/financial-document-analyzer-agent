# models.py
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

# ---------------- Pydantic v2 compatible ObjectId ---------------- #
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        return {"type": "string", "pattern": "^[0-9a-fA-F]{24}$"}

# ---------------- User Model ---------------- #
class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "validate_by_name": True
    }

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
