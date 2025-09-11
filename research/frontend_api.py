"""
Frontend API for Phase 4.
Provides HTTP endpoints for the React frontend to interact with video production.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import asyncio
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from .enhanced_content_pipeline import enhanced_content_pipeline
from .video_production import video_production_pipeline
from .db import init_db, get_citations_for_question
from .simple_vector_index import simple_vector_index
from .question_api_client import QuestionAPIClient
from .cache_manager import cache_manager
from .ultimate_slide_generator import ultimate_slide_generator

# Pydantic models for API requests/responses
class VideoGenerationRequest(BaseModel):
    question_id: str
    question: str
    solution: str

class VideoGenerationResponse(BaseModel):
    status: str
    question_id: str
    message: str
    estimated_time: Optional[int] = None
    job_id: Optional[str] = None

class VideoStatusResponse(BaseModel):
    status: str
    question_id: str
    progress: Optional[float] = None
    current_step: Optional[str] = None
    estimated_completion: Optional[str] = None
    video_file: Optional[str] = None
    error: Optional[str] = None

class QuestionData(BaseModel):
    id: str
    question: str
    solution: str
    subject: str
    difficulty: str
    options: List[str]
    correct_answer: int

# Sample questions for frontend testing
SAMPLE_QUESTIONS = [
    {
        "id": "ml_001",
        "question": "What is machine learning?",
        "solution": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
        "subject": "Machine Learning",
        "difficulty": "Beginner",
        "options": [
            "A programming language",
            "A subset of AI that learns from data",
            "A database system",
            "A web framework"
        ],
        "correct_answer": 1
    },
    {
        "id": "ml_002",
        "question": "What are the main types of machine learning?",
        "solution": "The main types are supervised learning, unsupervised learning, and reinforcement learning.",
        "subject": "Machine Learning",
        "difficulty": "Intermediate",
        "options": [
            "Web, Mobile, Desktop",
            "Supervised, Unsupervised, Reinforcement",
            "Frontend, Backend, Database",
            "Input, Process, Output"
        ],
        "correct_answer": 1
    },
    {
        "id": "ml_003",
        "question": "What is supervised learning?",
        "solution": "Supervised learning uses labeled training data to learn the mapping from inputs to outputs.",
        "subject": "Machine Learning",
        "difficulty": "Intermediate",
        "options": [
            "Learning without any data",
            "Learning with labeled training data",
            "Learning through trial and error",
            "Learning from user feedback"
        ],
        "correct_answer": 1
    }
]

# Global storage for video generation jobs
video_jobs = {}

app = FastAPI(
    title="NotebookLM Clone Frontend API",
    description="API for frontend integration with video production pipeline",
    version="1.0.0"
)

# Phase G: simple runtime metrics
_metrics = {
    "videos_started": 0,
    "videos_completed": 0,
    "videos_failed": 0,
    "avg_generate_ms": 0.0,
}

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video output
os.makedirs("video_output", exist_ok=True)
app.mount("/videos", StaticFiles(directory="video_output"), name="videos")

@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    print("🚀 Frontend API starting up...")
    
    # Phase G: environment checks
    try:
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"  ✅ FFmpeg found at {ffmpeg_path}")
        else:
            print("  ⚠️ FFmpeg not found in PATH. Install FFmpeg to ensure video rendering works.")
    except Exception:
        print("  ⚠️ Could not verify FFmpeg availability.")
    
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        print("  ✅ Playwright available for rasterization")
    except Exception as e:
        print(f"  ⚠️ Playwright not available ({e}). HTML rasterization will fall back to PIL where possible.")
    
    # Initialize database
    try:
        init_db("citations.db")
        print("  ✅ Database initialized")
    except Exception as e:
        print(f"  ⚠️ Database initialization warning: {e}")
    
    # Test video production pipeline
    try:
        video_status = video_production_pipeline.get_pipeline_status()
        print(f"  ✅ Video production pipeline: {video_status['status']}")
    except Exception as e:
        print(f"  ❌ Video production pipeline error: {e}")
    
    print("  🌐 Frontend API ready!")

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "NotebookLM Clone Frontend API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "questions": "/api/questions",
            "generate_video": "/api/generate-video",
            "video_status": "/api/video-status/{question_id}",
            "download_video": "/api/download-video/{question_id}",
            "health": "/api/health",
            "cache_stats": "/api/cache/stats",
            "cache_clear": "/api/cache/clear",
            "perf_settings": "/api/perf/settings",
            "perf_update": "/api/perf/update"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "video_pipeline": video_production_pipeline.get_pipeline_status()['status'],
            "enhanced_pipeline": enhanced_content_pipeline.get_pipeline_status()['status']
        },
        "cache": cache_manager.get_cache_stats(),
        "perf": {
            "slide_batch_size": ultimate_slide_generator.batch_size
        }
    }

@app.get("/api/questions", response_model=List[QuestionData])
async def get_questions(limit: int = 5, use_external: bool = True):
    """Get available questions for video generation.

    If use_external is True, fetch from external API; otherwise, return sample questions.
    """
    if use_external:
        try:
            client = QuestionAPIClient()
            questions = client.fetch_random_questions(limit)
            # Ensure the response matches QuestionData schema
            return [QuestionData(**q) for q in questions]
        except Exception as e:
            # Fallback to samples on failure
            print(f"⚠️ External questions fetch failed: {e}. Falling back to samples.")
            return SAMPLE_QUESTIONS[:limit]
    return SAMPLE_QUESTIONS[:limit]

@app.post("/api/generate-video", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Start video generation for a question."""
    try:
        # Check if video already exists
        video_file = f"video_output/video_{request.question_id}.mp4"
        if os.path.exists(video_file):
            return VideoGenerationResponse(
                status="already_exists",
                question_id=request.question_id,
                message="Video already exists for this question",
                video_file=video_file
            )
        
        # Create job entry
        job_id = f"job_{request.question_id}_{int(datetime.now().timestamp())}"
        video_jobs[request.question_id] = {
            "status": "queued",
            "job_id": job_id,
            "started_at": datetime.now().isoformat(),
            "progress": 0.0,
            "current_step": "Initializing...",
            "request": request.dict()
        }
        
        # Start background video generation
        _metrics["videos_started"] += 1
        background_tasks.add_task(
            generate_video_background,
            request.question_id,
            request.question,
            request.solution
        )
        
        return VideoGenerationResponse(
            status="started",
            question_id=request.question_id,
            message="Video generation started",
            estimated_time=120,  # 2 minutes estimate
            job_id=job_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start video generation: {str(e)}")

async def generate_video_background(question_id: str, question: str, solution: str):
    """Background task for video generation."""
    try:
        import time
        t0 = time.perf_counter()
        # Update job status
        video_jobs[question_id]["status"] = "running"
        video_jobs[question_id]["current_step"] = "Starting content generation..."
        video_jobs[question_id]["progress"] = 10.0
        
        # Connect to database for context search
        conn = sqlite3.connect('citations.db')
        
        # Generate video using enhanced pipeline
        result = await enhanced_content_pipeline.generate_complete_video(
            question_id=question_id,
            question=question,
            solution=solution,
            db_conn=conn
        )
        
        conn.close()
        
        if result['status'] == 'success':
            # Update job status to completed
            video_jobs[question_id]["status"] = "completed"
            video_jobs[question_id]["progress"] = 100.0
            video_jobs[question_id]["current_step"] = "Video generation completed"
            video_jobs[question_id]["video_file"] = result['video']['video_file']
            video_jobs[question_id]["completed_at"] = datetime.now().isoformat()
            t1 = time.perf_counter()
            # update metrics
            _metrics["videos_completed"] += 1
            delta_ms = (t1 - t0) * 1000
            # incremental average
            n = max(1, _metrics["videos_completed"])
            _metrics["avg_generate_ms"] = ((_metrics["avg_generate_ms"] * (n - 1)) + delta_ms) / n
            
            print(f"✅ Video generation completed for {question_id}")
        else:
            # Update job status to failed
            video_jobs[question_id]["status"] = "failed"
            video_jobs[question_id]["error"] = result.get('error', 'Unknown error')
            video_jobs[question_id]["current_step"] = "Video generation failed"
            _metrics["videos_failed"] += 1
            
            print(f"❌ Video generation failed for {question_id}: {result.get('error')}")
            
    except Exception as e:
        # Update job status to failed
        video_jobs[question_id]["status"] = "failed"
        video_jobs[question_id]["error"] = str(e)
        video_jobs[question_id]["current_step"] = "Video generation failed"
        _metrics["videos_failed"] += 1
        
        print(f"❌ Video generation crashed for {question_id}: {e}")

@app.get("/api/video-status/{question_id}", response_model=VideoStatusResponse)
async def get_video_status(question_id: str):
    """Get the status of video generation for a question."""
    if question_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Question not found")
    
    job = video_jobs[question_id]
    
    return VideoStatusResponse(
        status=job["status"],
        question_id=question_id,
        progress=job.get("progress", 0.0),
        current_step=job.get("current_step", "Unknown"),
        estimated_completion=job.get("estimated_completion"),
        video_file=job.get("video_file"),
        error=job.get("error")
    )

@app.get("/api/download-video/{question_id}")
async def download_video(question_id: str):
    """Download the generated video for a question."""
    video_file = f"video_output/video_{question_id}.mp4"
    
    if not os.path.exists(video_file):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_file,
        media_type="video/mp4",
        filename=f"video_{question_id}.mp4"
    )

@app.get("/api/video-preview/{question_id}")
async def get_video_preview(question_id: str):
    """Get video preview information."""
    video_file = f"video_output/video_{question_id}.mp4"
    manifest_file = f"video_output/manifest_{question_id}.json"
    
    if not os.path.exists(video_file):
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get video metadata
    video_info = {
        "question_id": question_id,
        "video_file": video_file,
        "file_size": os.path.getsize(video_file),
        "created_at": datetime.fromtimestamp(os.path.getctime(video_file)).isoformat()
    }
    
    # Get manifest if available
    if os.path.exists(manifest_file):
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                video_info.update({
                    "duration": manifest.get("total_duration"),
                    "slide_count": manifest.get("slide_count"),
                    "script_timing": manifest.get("script_timing")
                })
        except:
            pass
    
    return video_info

@app.get("/api/stats")
async def get_api_stats():
    """Get API usage statistics."""
    total_jobs = len(video_jobs)
    completed_jobs = len([j for j in video_jobs.values() if j["status"] == "completed"])
    failed_jobs = len([j for j in video_jobs.values() if j["status"] == "failed"])
    running_jobs = len([j for j in video_jobs.values() if j["status"] == "running"])
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "running_jobs": running_jobs,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/metrics")
async def get_metrics():
    """Return basic runtime metrics (Phase G)."""
    return {
        **_metrics,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics_prometheus():
    """Prometheus exposition format for runtime metrics (optional)."""
    lines = []
    lines.append("# HELP videos_started Total videos started")
    lines.append("# TYPE videos_started counter")
    lines.append(f"videos_started {_metrics['videos_started']}")
    lines.append("# HELP videos_completed Total videos completed successfully")
    lines.append("# TYPE videos_completed counter")
    lines.append(f"videos_completed {_metrics['videos_completed']}")
    lines.append("# HELP videos_failed Total videos that failed")
    lines.append("# TYPE videos_failed counter")
    lines.append(f"videos_failed {_metrics['videos_failed']}")
    lines.append("# HELP avg_generate_ms Average generation time in milliseconds")
    lines.append("# TYPE avg_generate_ms gauge")
    lines.append(f"avg_generate_ms {_metrics['avg_generate_ms']}")
    text = "\n".join(lines) + "\n"
    return JSONResponse(content=text, media_type="text/plain")

# Phase G: Cache endpoints
@app.get("/api/cache/stats")
async def get_cache_stats():
    return cache_manager.get_cache_stats()

@app.post("/api/cache/clear")
async def clear_cache(cache_type: Optional[str] = Query(None, description="research|raster|llm or empty for all")):
    cache_manager.clear_cache(cache_type)
    return {"status": "cleared", "type": cache_type or "all"}

# Phase G: Performance settings
class PerfSettings(BaseModel):
    slide_batch_size: Optional[int] = None

@app.get("/api/perf/settings")
async def get_perf_settings():
    return {
        "slide_batch_size": ultimate_slide_generator.batch_size
    }

@app.post("/api/perf/update")
async def update_perf_settings(settings: PerfSettings):
    if settings.slide_batch_size is not None:
        bs = max(1, min(12, int(settings.slide_batch_size)))
        ultimate_slide_generator.batch_size = bs
    return {
        "status": "updated",
        "slide_batch_size": ultimate_slide_generator.batch_size
    }

if __name__ == "__main__":
    uvicorn.run(
        "research.frontend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
