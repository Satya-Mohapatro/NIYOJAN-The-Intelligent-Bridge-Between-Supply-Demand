import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from ..agents.preprocessing import preprocess_forecast
from ..agents.rag import build_vector_store
from ..agents.graph import agent

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

# In-memory session store: { session_id: { forecast_data, vector_store, rag_available, warnings } }
_sessions: dict = {}


class QueryRequest(BaseModel):
    session_id: str
    query: str


@router.post("/upload")
async def upload_files(
    forecast_csv: UploadFile = File(...),
    report_pdf:   UploadFile = File(None),
):
    """
    Step 1: Upload forecast CSV (required) + report PDF (optional).
    Returns session_id to use for subsequent /query calls.
    """
    csv_bytes = await forecast_csv.read()
    pdf_bytes = await report_pdf.read() if report_pdf and report_pdf.filename else None

    try:
        forecast_data, warnings = preprocess_forecast(csv_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    vector_store, rag_available = build_vector_store(pdf_bytes)

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "forecast_data": forecast_data,
        "vector_store":  vector_store,
        "rag_available": rag_available,
        "warnings":      warnings,
    }

    return {
        "session_id":     session_id,
        "products_count": len(forecast_data),
        "rag_available":  rag_available,
        "warnings":       warnings,
        "products": [
            {
                "id":   p["product_id"],
                "name": p["product_name"],
                "risk": p["base_risk"],
                "gap":  p["inv_gap"],
            }
            for p in forecast_data
        ],
    }


@router.post("/query")
async def run_query(body: QueryRequest):
    """
    Step 2: Run a planning query against the uploaded data.
    Returns structured executive planning response.
    """
    session = _sessions.get(body.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload files first.",
        )

    initial_state = {
        "query":              body.query,
        "forecast_data":      session["forecast_data"],
        "_vector_store":      session["vector_store"],   # extra key — LangGraph passes it through
        "intent":             "",
        "simulation_percent": None,
        "rag_context":        [],
        "analysis_result":    {},
        "simulation_result":  {},
        "strategic_context":  {},
        "final_response":     {},
    }

    result = agent.invoke(initial_state)
    return result["final_response"]


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clean up session after user leaves."""
    _sessions.pop(session_id, None)
    return {"cleared": True}
