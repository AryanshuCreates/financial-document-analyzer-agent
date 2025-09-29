import os
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import aiofiles

from db import db, ensure_indexes
from task import analyze_document_and_save
from auth import verify_token, get_current_user
from models import AnalysisResponse, DocumentResponse, UserModel

load_dotenv()  
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await ensure_indexes()
    logger.info("Database indexes ensured")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Financial Document Analyzer",
    version="1.0.0",
    description="AI-powered financial document analysis API",
    lifespan=lifespan
)

# CORS - Configure for production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ALLOWED_ORIGINS in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data")

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

async def save_file(file: UploadFile, file_path: str) -> None:
    """Safely save uploaded file with size checking"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        total_size = 0
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    await aiofiles.os.remove(file_path)
                    raise HTTPException(status_code=413, detail="File too large")
                await out_file.write(chunk)
    except Exception as e:
        # Cleanup on failure
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
    """Upload and analyze financial document"""
    validate_file(file)
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    await save_file(file, file_path)
    
    # Save document metadata
    doc = {
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "path": file_path,
        "user_id": current_user.id,
        "status": "uploaded",
        "created_at": {"$currentDate": True}
    }
    
    try:
        res = await db.documents.insert_one(doc)
        document_id = str(res.inserted_id)
    except Exception as e:
        # Cleanup file if DB insert fails
        await aiofiles.os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Queue background analysis
    background_tasks.add_task(
        analyze_document_and_save, 
        document_id, 
        file_path, 
        query, 
        current_user.id
    )
    
    return DocumentResponse(
        status="queued",
        document_id=document_id,
        message="Document uploaded successfully and queued for analysis"
    )

@app.get("/analysis/{document_id}", response_model=AnalysisResponse)
async def get_analysis(
    document_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get analysis results for a document"""
    try:
        analysis = await db.analyses.find_one({
            "document_id": document_id,
            "user_id": current_user.id
        })
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisResponse(**analysis)
    except Exception as e:
        logger.error(f"Error retrieving analysis {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")

@app.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    current_user: UserModel = Depends(get_current_user)
):
    """List user's documents"""
    try:
        cursor = db.documents.find({"user_id": current_user.id}).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        logger.error(f"Error listing documents for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a document and its analysis"""
    try:
        # Find document
        doc = await db.documents.find_one({
            "_id": ObjectId(document_id),
            "user_id": current_user.id
        })
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file
        if os.path.exists(doc["path"]):
            await aiofiles.os.remove(doc["path"])
        
        # Delete from database
        await db.documents.delete_one({"_id": ObjectId(document_id)})
        await db.analyses.delete_many({"document_id": document_id})
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}