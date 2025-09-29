import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from crewai import Task
from agents import financial_analyst
from tools import read_financial_document, analyze_investment_text
from crew_runner import run_crew_async
from db import db

logger = logging.getLogger(__name__)

# ---------------- CrewAI Tasks ---------------- #
# Removed async_execution=True to prevent Crew errors
analyze_financial_document = Task(
    description="""
    Analyze the provided financial document text: {document_text}
    
    User Query: {query}
    
    Perform a comprehensive analysis including:
    1. Document type identification
    2. Key financial metrics extraction
    3. Summary of main findings
    4. Investment relevance assessment
    """,
    expected_output="""
    A structured analysis containing:
    - Document type and period covered
    - Key financial metrics (revenue, profit, cash flow, etc.)
    - Notable trends or changes
    - Investment insights based on the data
    - Data quality and completeness assessment
    """,
    agent=financial_analyst
)

investment_analysis = Task(
    description="""
    Based on the financial document analysis: {document_text}
    
    User Query: {query}
    
    Provide investment-focused recommendations including:
    1. Investment attractiveness assessment
    2. Strengths and weaknesses analysis  
    3. Comparison with industry benchmarks (if applicable)
    4. Recommendation rationale
    """,
    expected_output="""
    Investment analysis report with:
    - Investment recommendation (Buy/Hold/Sell) with confidence level
    - Key investment highlights and concerns
    - Financial strength indicators
    - Growth potential assessment
    - Recommended investment timeline
    """,
    agent=financial_analyst
)

risk_assessment = Task(
    description="""
    Conduct comprehensive risk analysis of the financial data: {document_text}
    
    User Query: {query}
    
    Identify and assess:
    1. Financial risks (liquidity, credit, market)
    2. Operational risks
    3. Industry-specific risks
    4. Risk mitigation strategies
    """,
    expected_output="""
    Risk assessment report with:
    - Identified risk categories and severity levels
    - Risk impact analysis
    - Risk probability assessments  
    - Recommended mitigation strategies
    - Overall risk score and rating
    """,
    agent=financial_analyst
)

verification_task = Task(
    description="""
    Verify the document classification and analysis quality: {document_text}
    
    Assess:
    1. Is this a legitimate financial document?
    2. Data quality and completeness
    3. Analysis reliability
    4. Potential limitations or caveats
    """,
    expected_output="""
    Verification report with:
    - Document authenticity assessment
    - Data quality score
    - Analysis confidence level
    - Identified limitations
    - Recommendations for additional analysis if needed
    """,
    agent=financial_analyst
)

# ---------------- Orchestrator ---------------- #
async def analyze_document_and_save(
    document_id: str,
    file_path: str,
    query: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main orchestrator for document analysis.
    Extracts text, performs local analysis, runs CrewAI tasks, saves results.
    """
    start_time = datetime.utcnow()

    try:
        # Update document status to processing
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"status": "processing", "processing_started_at": start_time}}
        )

        # Extract text
        doc_text = await read_financial_document(file_path)
        if not doc_text or len(doc_text.strip()) < 50:
            raise ValueError("Insufficient text extracted from document")

        # Local analysis
        local_summary = await analyze_investment_text(doc_text)

        # Run CrewAI
        crew_result = await run_crew_async(query, doc_text, timeout_s=300)

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        status = "completed" if "error" not in crew_result else "completed_with_errors"

        # Save analysis
        await db.analyses.insert_one({
            "document_id": document_id,
            "user_id": user_id,
            "query": query,
            "local_summary": local_summary,
            "crew_result": crew_result,
            "status": status,
            "processing_time_seconds": processing_time,
            "created_at": end_time,
            "text_length": len(doc_text)
        })

        # Update document status
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "status": "analyzed",
                    "analysis_completed_at": end_time,
                    "processing_time_seconds": processing_time
                }
            }
        )

        return {"status": status, "processing_time": processing_time}

    except Exception as e:
        error_time = datetime.utcnow()
        error_msg = str(e)

        # Save error record
        await db.analyses.insert_one({
            "document_id": document_id,
            "user_id": user_id,
            "query": query,
            "error": error_msg,
            "status": "failed",
            "created_at": error_time
        })
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"status": "failed", "error": error_msg, "failed_at": error_time}}
        )

        return {"status": "failed", "error": error_msg}
