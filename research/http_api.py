"""
HTTP API for Phase 2 Context Search.
Provides FastAPI endpoints for RAG retrieval and context search.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
from .enhanced_vector_index import enhanced_vector_index
from .db import init_db


# Pydantic models for API responses
class ContextSearchResult(BaseModel):
    rank: int
    score: float
    url: str
    title: str
    site_name: str
    heading: str
    content: str
    page: Optional[int] = None
    source_info: str
    ranking_details: Dict[str, float]


class ContextSearchResponse(BaseModel):
    query: str
    results: List[ContextSearchResult]
    total_results: int
    index_stats: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    status: str
    index_stats: Dict[str, Any]
    database_status: str


# Initialize FastAPI app
app = FastAPI(
    title="Research Context Search API",
    description="HTTP API for RAG retrieval and context search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Research Context Search API",
        "version": "1.0.0",
        "endpoints": {
            "context_search": "/ctx/search",
            "health": "/health",
            "index_stats": "/index/stats"
        }
    }


@app.get("/ctx/search", response_model=ContextSearchResponse)
async def context_search(
    q: str = Query(..., description="Search query"),
    k: int = Query(12, description="Number of results to return", ge=1, le=50),
    weights: Optional[str] = Query(None, description="Custom ranking weights (JSON string)")
):
    """
    Search for relevant context using hybrid ranking.
    
    - **q**: Search query
    - **k**: Number of results (1-50)
    - **weights**: Optional custom ranking weights
    """
    try:
        # Parse custom weights if provided
        custom_weights = None
        if weights:
            import json
            try:
                custom_weights = json.loads(weights)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid weights JSON")
        
        # Initialize database connection
        db_conn = init_db()
        
        try:
            # Perform hybrid search
            search_results = enhanced_vector_index.search_with_context(q, k, db_conn)
            
            # Convert to Pydantic models
            context_results = []
            for result in search_results:
                context_result = ContextSearchResult(
                    rank=result['rank'],
                    score=result['score'],
                    url=result['url'],
                    title=result['title'],
                    site_name=result['site_name'],
                    heading=result['heading'],
                    content=result['content'],
                    page=result.get('page'),
                    source_info=result['source_info'],
                    ranking_details=result.get('ranking_details', {})
                )
                context_results.append(context_result)
            
            # Get index statistics
            index_stats = enhanced_vector_index.get_index_stats()
            
            return ContextSearchResponse(
                query=q,
                results=context_results,
                total_results=len(context_results),
                index_stats=index_stats
            )
            
        finally:
            db_conn.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check index status
        index_stats = enhanced_vector_index.get_index_stats()
        
        # Check database status
        try:
            db_conn = init_db()
            db_conn.execute("SELECT 1")
            db_status = "healthy"
            db_conn.close()
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        return HealthCheckResponse(
            status="healthy",
            index_stats=index_stats,
            database_status=db_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/index/stats", response_model=Dict[str, Any])
async def get_index_stats():
    """Get detailed index statistics."""
    try:
        return enhanced_vector_index.get_index_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get index stats: {str(e)}")


@app.post("/index/rebuild")
async def rebuild_index():
    """Rebuild the vector index from database content."""
    try:
        db_conn = init_db()
        try:
            sections_added = enhanced_vector_index.rebuild_index(db_conn)
            return {
                "message": "Index rebuild completed",
                "sections_added": sections_added
            }
        finally:
            db_conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(e)}")


@app.get("/search/hybrid", response_model=List[Dict[str, Any]])
async def hybrid_search(
    q: str = Query(..., description="Search query"),
    k: int = Query(12, description="Number of results", ge=1, le=50),
    vector_weight: float = Query(0.55, description="Vector similarity weight", ge=0.0, le=1.0),
    bm25_weight: float = Query(0.25, description="BM25 weight", ge=0.0, le=1.0),
    credibility_weight: float = Query(0.15, description="Credibility weight", ge=0.0, le=1.0),
    freshness_weight: float = Query(0.05, description="Freshness weight", ge=0.0, le=1.0)
):
    """
    Advanced hybrid search with custom weights.
    
    - **q**: Search query
    - **k**: Number of results
    - **vector_weight**: Weight for vector similarity (0.0-1.0)
    - **bm25_weight**: Weight for BM25 ranking (0.0-1.0)
    - **credibility_weight**: Weight for source credibility (0.0-1.0)
    - **freshness_weight**: Weight for content freshness (0.0-1.0)
    """
    try:
        # Validate weights sum to 1.0
        total_weight = vector_weight + bm25_weight + credibility_weight + freshness_weight
        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=400, 
                detail=f"Weights must sum to 1.0, got {total_weight}"
            )
        
        # Initialize database connection
        db_conn = init_db()
        
        try:
            # Custom weights
            weights = {
                'vector': vector_weight,
                'bm25': bm25_weight,
                'credibility': credibility_weight,
                'freshness': freshness_weight
            }
            
            # Perform hybrid search with custom weights
            search_results = enhanced_vector_index.search_hybrid(q, k, db_conn, weights)
            
            return search_results
            
        finally:
            db_conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")


def run_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    uvicorn.run(
        "research.http_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_api_server()
