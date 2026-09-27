import time
import os
from pathlib import Path
from typing import Set, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from domain.models import (
    ProcessRequest, ProcessResponse, ArticleDraft, AuditReport, PipelineStatus
)
from infrastructure.heuristic_linter import HeuristicRoboticLinter, CLICHE_REPLACEMENTS
from infrastructure.ddg_plagiarism import DuckDuckGoPlagiarismChecker
from infrastructure.language_tool import LanguageToolGrammarChecker
from infrastructure.gemini_client import GeminiClient
from infrastructure.gemini_translator import GeminiTranslator
from infrastructure.orwell_humanizer import OrwellHumanizer
from application.audit_aggregator import AuditAggregator
from application.orchestrator import PipelineOrchestrator
from application.semantic_guard import SemanticPreservationGuard


app = FastAPI(
    title="Carik Editorial Studio",
    description="Autonomous Humanized Editorial Pipeline API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_websockets: Set[WebSocket] = set()


async def broadcast_ws(event_type: str, data: Dict[str, Any]) -> None:
    dead_connections = set()
    payload = {"event": event_type, "data": data}
    for ws in connected_websockets:
        try:
            await ws.send_json(payload)
        except Exception:
            dead_connections.add(ws)
    connected_websockets.difference_update(dead_connections)


def create_orchestrator(max_retries: int = 3, api_key: Optional[str] = None) -> PipelineOrchestrator:
    gemini_client = GeminiClient(api_key=api_key)
    translator = GeminiTranslator(gemini_client)
    humanizer = OrwellHumanizer(gemini_client)
    plag_checker = DuckDuckGoPlagiarismChecker()
    grammar_checker = LanguageToolGrammarChecker()
    robotic_linter = HeuristicRoboticLinter()
    
    auditor = AuditAggregator(plag_checker, grammar_checker, robotic_linter)
    semantic_guard = SemanticPreservationGuard()
    
    return PipelineOrchestrator(
        translator=translator,
        auditor=auditor,
        humanizer=humanizer,
        semantic_guard=semantic_guard,
        max_retries=max_retries
    )


@app.get("/api/v1/health")
async def health_check():
    gemini_client = GeminiClient()
    return {
        "status": "healthy",
        "gemini_active": gemini_client.is_configured,
        "gemini_model": gemini_client.model_name
    }


@app.get("/api/v1/cliches")
async def get_cliches():
    return {
        "banned_count": len(CLICHE_REPLACEMENTS),
        "cliches": CLICHE_REPLACEMENTS
    }


@app.post("/api/v1/audit-only", response_model=AuditReport)
async def audit_text_only(payload: Dict[str, str]):
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    plag_checker = DuckDuckGoPlagiarismChecker()
    grammar_checker = LanguageToolGrammarChecker()
    robotic_linter = HeuristicRoboticLinter()
    auditor = AuditAggregator(plag_checker, grammar_checker, robotic_linter)
    
    return await auditor.evaluate(text, iteration=1)


@app.post("/api/v1/process", response_model=ProcessResponse)
async def process_article(req: ProcessRequest):
    start_time = time.time()
    orchestrator = create_orchestrator(max_retries=req.max_retries, api_key=req.api_key)
    draft = ArticleDraft(original_bahasa=req.text)
    
    async def ws_callback(event: str, data: dict):
        await broadcast_ws(event, data)

    final_draft = await orchestrator.run(draft, callback=ws_callback)
    duration = time.time() - start_time
    
    return ProcessResponse(
        success=(final_draft.status == PipelineStatus.PASSED),
        final_draft=final_draft,
        processing_time_sec=round(duration, 2)
    )


@app.websocket("/ws/pipeline-progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)
    except Exception:
        connected_websockets.discard(websocket)


static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def serve_index():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Carik Editorial API running."}
