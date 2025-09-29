import asyncio
import logging
from typing import Dict, Any
from crewai import Crew, Process
from agents import financial_analyst

logger = logging.getLogger(__name__)

async def run_crew_async(
    query: str, 
    document_text: str, 
    timeout_s: int = 300
) -> Dict[str, Any]:
    """
    Run CrewAI analysis and return structured results.
    """
    from task import (
        analyze_financial_document,
        investment_analysis,
        risk_assessment,
        verification_task,
    )

    crew = Crew(
        agents=[financial_analyst],
        tasks=[
            analyze_financial_document,
            investment_analysis,
            risk_assessment,
            verification_task,
        ],
        process=Process.sequential,
        verbose=True
    )
    
    try:
        logger.info("Starting CrewAI analysis")
        inputs = {
            "query": query,
            "document_text": document_text[:10000]
        }
        
        result = await asyncio.wait_for(
            asyncio.to_thread(crew.kickoff, inputs),
            timeout=timeout_s
        )

        # Parse Crew result into structured dict
        structured_result = {}
        for task_name, task_output in result.items():
            # Convert Crew Output object to string or dict
            try:
                structured_result[task_name] = task_output.output  # most Crew tasks store output here
            except AttributeError:
                structured_result[task_name] = str(task_output)
        
        logger.info("CrewAI analysis completed successfully")
        return {"result": structured_result, "status": "success"}
        
    except asyncio.TimeoutError:
        error_msg = f"CrewAI analysis timed out after {timeout_s} seconds"
        logger.error(error_msg)
        return {"error": "timeout", "message": error_msg}
        
    except Exception as e:
        error_msg = f"CrewAI analysis failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": "crew_failure", "message": error_msg}
