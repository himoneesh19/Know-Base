from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from pathlib import Path
from dotenv import load_dotenv

from kb_manager import KBManager

# Load environment variables
load_dotenv()

app = FastAPI(title="KnowBase", description="AI-powered searchable knowledge base")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the knowledge base manager
try:
    kb_manager = KBManager(kb_path="./knowledge_base")
except ValueError as e:
    print(f"Warning: {e}")
    kb_manager = None


# Request/Response models
class IngestRequest(BaseModel):
    filepath: str


class QueryRequest(BaseModel):
    question: str


class HealthResponse(BaseModel):
    status: str


class QueryResponse(BaseModel):
    answer: str


class DocumentInfo(BaseModel):
    name: str
    path: str
    size: int


# REST Endpoints

@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/ingest")
async def ingest_document(request: IngestRequest) -> dict:
    """
    Ingest a markdown document into the knowledge base.
    
    Args:
        request: Contains the filepath to the markdown document
        
    Returns:
        Success or error message
    """
    if kb_manager is None:
        raise HTTPException(status_code=500, detail="Knowledge base not initialized. Set OPENROUTER_API_KEY.")
    
    try:
        filepath = request.filepath
        
        # Check if it's an absolute path, if not make it relative to current directory
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)
        
        # Verify file exists
        if not os.path.exists(filepath):
            raise HTTPException(status_code=400, detail=f"File not found: {filepath}")
        
        # Add document to knowledge base
        success = kb_manager.add_document(filepath)
        
        if success:
            return {
                "status": "success",
                "message": f"Document {os.path.basename(filepath)} ingested successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to ingest document")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    """
    Upload a markdown or PDF file directly from the browser.
    """
    if kb_manager is None:
        raise HTTPException(status_code=500, detail="Knowledge base not initialized. Set OPENROUTER_API_KEY.")

    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

        contents = await file.read()
        success = kb_manager.add_document_from_upload(contents, file.filename)

        if success:
            return {
                "status": "success",
                "message": f"Document {file.filename} ingested successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to ingest uploaded document")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    """
    Query the knowledge base with a natural language question.
    
    Args:
        request: Contains the question
        
    Returns:
        Answer synthesized from the knowledge base
    """
    if kb_manager is None:
        raise HTTPException(status_code=500, detail="Knowledge base not initialized. Set OPENROUTER_API_KEY.")
    
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        answer = kb_manager.query(request.question)
        return QueryResponse(answer=answer)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents() -> dict:
    """
    Get list of all ingested documents.
    
    Returns:
        List of document information
    """
    if kb_manager is None:
        return {"documents": [], "count": 0}
    
    try:
        documents = kb_manager.list_documents()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file."""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    
    if frontend_path.exists():
        return FileResponse(frontend_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


# Mount static files if needed
static_path = Path(__file__).parent / "frontend"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
