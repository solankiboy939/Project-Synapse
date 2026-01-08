"""
API routes for Project Synapse
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel

from ..models import (
    UserContext, SiloMetadata, QueryRequest, KnowledgeResult, 
    SynthesisOutput, IndexingJob, AccessLevel, SiloType
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class IndexSiloRequest(BaseModel):
    silo_metadata: SiloMetadata


class QueryResponse(BaseModel):
    results: List[KnowledgeResult]
    total_results: int
    query_time_ms: float
    privacy_budget_used: float


class SynthesisRequest(BaseModel):
    query: str
    user_context: UserContext
    result_ids: List[str]  # IDs of results to synthesize


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    privacy_budget_remaining: float


# Dependency to get components from app state
def get_federated_indexer(request: Request):
    return request.app.state.federated_indexer


def get_query_engine(request: Request):
    return request.app.state.query_engine


def get_synthesizer(request: Request):
    return request.app.state.synthesizer


def get_privacy_manager(request: Request):
    return request.app.state.privacy_manager


def get_encryption_manager(request: Request):
    return request.app.state.encryption_manager


@router.post("/silos/index", response_model=IndexingJob)
async def index_silo(
    request: IndexSiloRequest,
    background_tasks: BackgroundTasks,
    indexer=Depends(get_federated_indexer)
):
    """Index a new silo or update existing silo index"""
    
    try:
        # Start indexing in background
        job = await indexer._index_silo(request.silo_metadata)
        
        logger.info(f"Started indexing job for silo {request.silo_metadata.silo_id}")
        return job
        
    except Exception as e:
        logger.error(f"Failed to start indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/silos", response_model=List[SiloMetadata])
async def list_silos(
    user_context: UserContext = None,
    indexer=Depends(get_federated_indexer)
):
    """List all silos accessible to the user"""
    
    try:
        # Get all silo metadata
        all_silos = []
        for silo_id, silo_data in indexer.silo_indexes.items():
            all_silos.append(silo_data["metadata"])
            
        # Filter by user permissions if context provided
        if user_context:
            from ..security import PermissionEngine
            permission_engine = PermissionEngine()
            accessible_silos = permission_engine.get_accessible_silos(user_context, all_silos)
            return accessible_silos
            
        return all_silos
        
    except Exception as e:
        logger.error(f"Failed to list silos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def federated_query(
    query_request: QueryRequest,
    query_engine=Depends(get_query_engine)
):
    """Execute federated query across silos"""
    
    import time
    start_time = time.time()
    
    try:
        # Execute federated query
        results = await query_engine.route_query(query_request)
        
        query_time_ms = (time.time() - start_time) * 1000
        
        response = QueryResponse(
            results=results,
            total_results=len(results),
            query_time_ms=query_time_ms,
            privacy_budget_used=query_request.privacy_budget
        )
        
        logger.info(f"Query completed: {len(results)} results in {query_time_ms:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize", response_model=SynthesisOutput)
async def synthesize_knowledge(
    synthesis_request: SynthesisRequest,
    synthesizer=Depends(get_synthesizer),
    query_engine=Depends(get_query_engine)
):
    """Synthesize knowledge from multiple results"""
    
    try:
        # First execute query to get results
        query_request = QueryRequest(
            query=synthesis_request.query,
            user_context=synthesis_request.user_context,
            max_results=20  # Get more results for synthesis
        )
        
        results = await query_engine.route_query(query_request)
        
        # Filter to requested result IDs if specified
        if synthesis_request.result_ids:
            results = [r for r in results if r.result_id in synthesis_request.result_ids]
            
        # Synthesize knowledge
        synthesis = await synthesizer.synthesize_answers(
            synthesis_request.query,
            results,
            synthesis_request.user_context
        )
        
        logger.info(f"Synthesis completed for query: {synthesis_request.query[:50]}...")
        return synthesis
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_query_suggestions(
    partial_query: str,
    user_context: UserContext,
    query_engine=Depends(get_query_engine)
):
    """Get query suggestions based on accessible content"""
    
    try:
        suggestions = await query_engine.get_query_suggestions(partial_query, user_context)
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/privacy/report")
async def get_privacy_report(
    privacy_manager=Depends(get_privacy_manager)
):
    """Get privacy budget usage report"""
    
    try:
        report = privacy_manager.get_privacy_report()
        return report
        
    except Exception as e:
        logger.error(f"Failed to get privacy report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/privacy/reset")
async def reset_privacy_budget(
    privacy_manager=Depends(get_privacy_manager)
):
    """Reset privacy budget (admin only)"""
    
    try:
        privacy_manager.reset_privacy_budget()
        return {"message": "Privacy budget reset successfully"}
        
    except Exception as e:
        logger.error(f"Failed to reset privacy budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/encryption/status")
async def get_encryption_status(
    encryption_manager=Depends(get_encryption_manager)
):
    """Get encryption key status"""
    
    try:
        status = encryption_manager.get_encryption_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get encryption status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encryption/keys/{silo_id}")
async def generate_silo_keys(
    silo_id: str,
    encryption_manager=Depends(get_encryption_manager)
):
    """Generate encryption keys for a silo"""
    
    try:
        keys = encryption_manager.generate_silo_keys(silo_id)
        return keys
        
    except Exception as e:
        logger.error(f"Failed to generate keys for silo {silo_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/detailed", response_model=HealthResponse)
async def detailed_health_check(
    indexer=Depends(get_federated_indexer),
    query_engine=Depends(get_query_engine),
    synthesizer=Depends(get_synthesizer),
    privacy_manager=Depends(get_privacy_manager)
):
    """Detailed health check of all components"""
    
    try:
        components = {
            "federated_indexer": "healthy" if indexer else "unhealthy",
            "query_engine": "healthy" if query_engine else "unhealthy", 
            "synthesizer": "healthy" if synthesizer else "unhealthy",
            "privacy_manager": "healthy" if privacy_manager else "unhealthy"
        }
        
        overall_status = "healthy" if all(
            status == "healthy" for status in components.values()
        ) else "degraded"
        
        privacy_budget_remaining = privacy_manager.get_remaining_budget() if privacy_manager else 0.0
        
        return HealthResponse(
            status=overall_status,
            components=components,
            privacy_budget_remaining=privacy_budget_remaining
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_system_stats(
    indexer=Depends(get_federated_indexer)
):
    """Get system statistics"""
    
    try:
        total_silos = len(indexer.silo_indexes)
        total_documents = sum(
            silo_data["document_count"] 
            for silo_data in indexer.silo_indexes.values()
        )
        
        silo_types = {}
        for silo_data in indexer.silo_indexes.values():
            silo_type = silo_data["metadata"].silo_type
            silo_types[silo_type] = silo_types.get(silo_type, 0) + 1
            
        return {
            "total_silos": total_silos,
            "total_documents": total_documents,
            "silo_types": silo_types,
            "global_index": indexer.global_index
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))