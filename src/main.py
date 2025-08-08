# src/main.py

from fastapi import FastAPI, Depends, HTTPException
import logging, requests
from typing import Optional

from .models import HackRxRunRequest, HackRxRunResponse
from .auth import get_optional_api_key
from .rag import process_document_and_answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ultrafast Local RAG API (FAISS)",
    description="Processes documents using a local in-memory FAISS index with semantic chunking.",
    version="6.0.0"
)

@app.post("/hackrx/run", response_model=HackRxRunResponse)
async def run_pipeline(
    request: HackRxRunRequest,
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """
    Processes a document and returns answers directly. This is a blocking call
    but is now very fast as it uses a local vector index.
    """
    doc_location = request.documents
    pdf_bytes = None

    try:
        if doc_location.startswith(('http://', 'https://')):
            response = requests.get(doc_location)
            response.raise_for_status()
            pdf_bytes = response.content
        else:
            with open(doc_location, "rb") as f:
                pdf_bytes = f.read()
        
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Could not load document content.")

        answers = await process_document_and_answer(
            pdf_bytes=pdf_bytes,
            questions=request.questions,
            api_key=api_key
        )
        
        return HackRxRunResponse(answers=answers)

    except FileNotFoundError:
        raise HTTPException(status_code=400, detail=f"Local file not found at path: {doc_location}")
    except Exception as e:
        logger.error(f"An error occurred during pipeline execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API is running"}