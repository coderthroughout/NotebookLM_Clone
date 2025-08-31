"""
Simple HTTP API for Research Context Search.
Uses the dependency-free simple_vector_index.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
from .simple_vector_index import simple_vector_index
from .db import init_db
import sqlite3

# Pydantic models for API requests/responses
class SearchRequest(BaseModel):
    query: str
    k: int = 12
    weights: Optional[Dict[str, float]] = None

class SearchResult(BaseModel):
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

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    index_stats: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    index_stats: Dict[str, Any]

class IndexStatsResponse(BaseModel):
    index_stats: Dict[str, Any]
    database_stats: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="Simple Research Context Search API",
    description="HTTP API for RAG retrieval using OpenAI embeddings (dependency-free)",
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
        "message": "Simple Research Context Search API",
        "version": "1.0.0",
        "embedding_model": "OpenAI text-embedding-3-small",
        "vector_index": "Simple OpenAI + Cosine Similarity",
        "endpoints": {
            "context_search": "/ctx/search",
            "health": "/health",
            "index_stats": "/index/stats",
            "embedding_test": "/embedding/test"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        index_stats=simple_vector_index.get_index_stats()
    )

@app.get("/index/stats", response_model=IndexStatsResponse)
async def get_index_stats():
    """Get detailed statistics about the vector index and database."""
    # Get index stats
    index_stats = simple_vector_index.get_index_stats()
    
    # Get database stats
    try:
        db_path = "citations.db"  # Default path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count documents and sections
        cursor.execute("SELECT COUNT(*) FROM normalized_doc")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM section")
        section_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM citations")
        citation_count = cursor.fetchone()[0]
        
        conn.close()
        
        database_stats = {
            "total_documents": doc_count,
            "total_sections": section_count,
            "total_citations": citation_count,
            "database_path": db_path
        }
    except Exception as e:
        database_stats = {
            "error": str(e),
            "database_path": "unknown"
        }
    
    return IndexStatsResponse(
        index_stats=index_stats,
        database_stats=database_stats
    )

@app.post("/ctx/search", response_model=SearchResponse)
async def search_context(request: SearchRequest):
    """
    Search for context using the simple vector index.
    Returns ranked results with full context for LLM consumption.
    """
    try:
        # Validate query
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get database connection
        db_path = "citations.db"
        conn = sqlite3.connect(db_path)
        
        # Perform search
        results = await simple_vector_index.search_with_context(
            query=request.query,
            k=request.k,
            db_conn=conn
        )
        
        conn.close()
        
        # Convert to Pydantic models
        search_results = []
        for result in results:
            search_result = SearchResult(
                rank=result['rank'],
                score=result['score'],
                url=result['url'],
                title=result['title'],
                site_name=result['site_name'],
                heading=result['heading'],
                content=result['content'],
                page=result['page'],
                source_info=result['source_info'],
                ranking_details=result['ranking_details']
            )
            search_results.append(search_result)
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            index_stats=simple_vector_index.get_index_stats()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/ctx/search", response_model=SearchResponse)
async def search_context_get(
    q: str = Query(..., description="Search query"),
    k: int = Query(12, description="Number of results to return")
):
    """
    GET endpoint for context search (alternative to POST).
    """
    request = SearchRequest(query=q, k=k)
    return await search_context(request)

@app.post("/embedding/test")
async def test_embedding():
    """
    Test OpenAI embedding generation.
    """
    try:
        from .llm import llm_client
        
        # Test text
        test_texts = ["This is a test sentence for embedding generation."]
        
        # Generate embeddings
        embeddings = await llm_client.get_embeddings(test_texts)
        
        if embeddings and len(embeddings) > 0:
            embedding = embeddings[0]
            return {
                "status": "success",
                "message": "OpenAI embedding generation working",
                "embedding_dimension": len(embedding),
                "sample_values": embedding[:5] if len(embedding) >= 5 else embedding
            }
        else:
            return {
                "status": "error",
                "message": "No embeddings generated"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Embedding test failed: {str(e)}"
        }

@app.post("/index/rebuild")
async def rebuild_index():
    """
    Rebuild the entire vector index from database content.
    """
    try:
        # Get database connection
        db_path = "citations.db"
        conn = sqlite3.connect(db_path)
        
        # Rebuild index
        sections_added = await simple_vector_index.rebuild_index(conn)
        
        conn.close()
        
        return {
            "status": "success",
            "message": f"Index rebuilt successfully",
            "sections_added": sections_added,
            "index_stats": simple_vector_index.get_index_stats()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(e)}")

@app.get("/search/simple")
async def simple_search(
    q: str = Query(..., description="Search query"),
    k: int = Query(5, description="Number of results to return")
):
    """
    Simple search endpoint for testing.
    """
    try:
        # Get database connection
        db_path = "citations.db"
        conn = sqlite3.connect(db_path)
        
        # Perform simple search
        results = await simple_vector_index.search_with_context(
            query=q,
            k=k,
            db_conn=conn
        )
        
        conn.close()
        
        # Return simplified results
        simplified_results = []
        for result in results:
            simplified_results.append({
                "rank": result['rank'],
                "score": round(result['score'], 3),
                "title": result['title'],
                "site": result['site_name'],
                "heading": result['heading'],
                "content_preview": result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            })
        
        return {
            "query": q,
            "results": simplified_results,
            "total_found": len(simplified_results)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": q
        }

if __name__ == "__main__":
    # Initialize database
    init_db("citations.db")
    
    # Run the API server
    uvicorn.run(
        "research.http_api_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
