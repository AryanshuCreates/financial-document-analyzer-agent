# db.py
import os
import logging
from datetime import datetime
from typing import Optional  
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from dotenv import load_dotenv
from bson import ObjectId
from pydantic import BaseModel, Field

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------- Pydantic v2 compatible ObjectId ---------------- #
class PyObjectId(ObjectId):
    """
    BSON ObjectId wrapper compatible with Pydantic v2
    """
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema):
        from pydantic import core_schema
        return core_schema.str_schema()

# ---------------- MongoDB Connection ---------------- #
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable must be set")

client = AsyncIOMotorClient(MONGO_URI, uuidRepresentation='standard')
db = client[os.getenv("DB_NAME", "financial_analyzer")]

# ---------------- Index Management ---------------- #
async def ensure_indexes():
    """Create database indexes"""
    try:
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.documents.create_index([("user_id", ASCENDING)])
        await db.documents.create_index([("file_id", ASCENDING)], unique=True)
        await db.analyses.create_index([("document_id", ASCENDING)])
        await db.analyses.create_index([("user_id", ASCENDING)])
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise

# ---------------- Connection Test ---------------- #
async def check_db_connection():
    """Check database connection"""
    try:
        await client.admin.command('ping')
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# ---------------- Pydantic Models for DB ---------------- #
class DocumentModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    file_id: str
    status: str
    metadata: dict = {}

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class AnalysisModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: str
    user_id: Optional[str] = None  # now Optional is defined
    query: str
    local_summary: dict
    crew_result: dict
    status: str
    processing_time_seconds: float
    created_at: datetime
    text_length: int

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
