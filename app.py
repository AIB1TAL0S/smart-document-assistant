from pathlib import Path
import os

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from engine import Engine

ROOT = Path(__file__).resolve().parent
MAX_UPLOAD = 20 * 1024 * 1024
engine = Engine(Path(os.environ.get("DATA_DIR", ROOT / "data")))
app = FastAPI(title="Smart Document Assistant")


@app.middleware("http")
async def local_requests(request: Request, call_next):
    # Block cross-origin writes and DNS rebinding against this unauthenticated local app.
    if request.url.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return JSONResponse({"detail": "Only localhost access is allowed."}, status_code=403)
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        return JSONResponse({"detail": "Cross-origin requests are not allowed."}, status_code=403)
    return await call_next(request)


@app.exception_handler(ValueError)
async def input_error(request: Request, exc: ValueError):
    return JSONResponse({"detail": str(exc)}, status_code=400)


@app.exception_handler(RuntimeError)
async def model_error(request: Request, exc: RuntimeError):
    return JSONResponse({"detail": str(exc)}, status_code=503)


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/documents")
def documents():
    return {"documents": engine.documents()}


@app.post("/api/documents", status_code=201)
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read(MAX_UPLOAD + 1)
        if len(content) > MAX_UPLOAD:
            raise HTTPException(413, "Maximum document size is 20 MiB.")
        return await run_in_threadpool(engine.ingest, Path(file.filename or "document").name, content)
    finally:
        await file.close()


@app.delete("/api/documents/{document_id}")
def delete(document_id: str):
    if not engine.delete(document_id):
        raise HTTPException(404, "Document not found.")
    return {"deleted": True}


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


@app.post("/api/ask")
def ask(body: Question):
    return engine.ask(body.question)
