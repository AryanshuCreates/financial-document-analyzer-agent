import os
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Optional, List
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import aiofiles
from bson import ObjectId
from pydantic import BaseModel

from db import db, ensure_indexes
from task import analyze_document_and_save
from auth import get_current_user, hash_password, verify_password, create_access_token
from models import AnalysisResponse, DocumentResponse, UserModel

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    logger.info("Database indexes ensured")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Financial Document Analyzer",
    version="1.0.0",
    description="AI-powered financial document analysis API",
    lifespan=lifespan
)

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data")

# ----------------------- Helper ----------------------- #
def convert_objectids(doc: dict, fields: list[str]):
    for field in fields:
        if field in doc and isinstance(doc[field], ObjectId):
            doc[field] = str(doc[field])
    return doc

# ----------------------- User Auth Models ----------------------- #
class RegisterRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "viewer"

class LoginRequest(BaseModel):
    email: str
    password: str

# ----------------------- Auth Endpoints ----------------------- #
@app.post("/register")
async def register_user(req: RegisterRequest):
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = req.role.lower() if req.role and req.role.lower() in ["admin", "viewer"] else "viewer"
    user_doc = {
        "email": req.email,
        "password": hash_password(req.password),
        "role": role
    }

    res = await db.users.insert_one(user_doc)
    user_doc["_id"] = str(res.inserted_id)
    token = create_access_token({"sub": user_doc["_id"], "role": user_doc["role"]})
    return {"access_token": token, "role": user_doc["role"], "email": user_doc["email"]}

@app.post("/login")
async def login_user(req: LoginRequest):
    user = await db.users.find_one({"email": req.email})
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    return {"access_token": token, "role": user["role"], "email": user["email"]}

# ----------------------- File Endpoints ----------------------- #
def validate_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}")

async def save_file(file: UploadFile, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        total_size = 0
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    await aiofiles.os.remove(file_path)
                    raise HTTPException(status_code=413, detail="File too large")
                await out_file.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            await aiofiles.os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

@app.post("/analyze", response_model=DocumentResponse)
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    current_user: UserModel = Depends(get_current_user),
):
    validate_file(file)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    await save_file(file, file_path)

    doc = {
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "path": file_path,
        "user_id": str(current_user.id),
        "status": "uploaded",
        "created_at": {"$currentDate": True}
    }

    try:
        res = await db.documents.insert_one(doc)
        document_id = str(res.inserted_id)
    except Exception as e:
        await aiofiles.os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    background_tasks.add_task(
        analyze_document_and_save,
        document_id,
        file_path,
        query,
        str(current_user.id)
    )

    return DocumentResponse(
        status="queued",
        document_id=document_id,
        message="Document uploaded successfully and queued for analysis"
    )

@app.get("/analyses/{document_id}", response_model=List[AnalysisResponse])
async def get_analyses(document_id: str, current_user: UserModel = Depends(get_current_user)):
    query = {"document_id": document_id}
    if current_user.role != "admin":
        query["user_id"] = str(current_user.id)

    cursor = db.analyses.find(query).sort("created_at", -1)
    analyses = []
    async for doc in cursor:
        analyses.append(convert_objectids(doc, ["_id", "user_id"]))
    
    if not analyses:
        raise HTTPException(status_code=404, detail="No analyses found")
    
    return analyses

@app.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    current_user: UserModel = Depends(get_current_user)
):
    query = {} if current_user.role == "admin" else {"user_id": str(current_user.id)}
    cursor = db.documents.find(query).skip(skip).limit(limit).sort("created_at", -1)
    documents = await cursor.to_list(length=limit)
    documents = [convert_objectids(doc, ["_id", "user_id"]) for doc in documents]
    total = await db.documents.count_documents(query)
    return {"documents": documents, "total": total}

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    doc = await db.documents.find_one({
        "_id": ObjectId(document_id),
        **({} if current_user.role == "admin" else {"user_id": str(current_user.id)})
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if os.path.exists(doc["path"]):
        await aiofiles.os.remove(doc["path"])
    await db.documents.delete_one({"_id": ObjectId(document_id)})
    await db.analyses.delete_many({"document_id": document_id})
    return {"message": "Document deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
