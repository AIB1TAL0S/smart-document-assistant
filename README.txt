Smart Document Assistant
========================
Local PDF/DOCX/TXT questions using Ollama embeddings, SQLite retrieval and local answer generation. No cloud API keys, external frontend assets or hosted vector database.

Quick start
-----------
Install Python 3.11+, uv (https://docs.astral.sh/uv/) and Ollama (https://ollama.com/).
In one terminal:
  OLLAMA_NO_CLOUD=1 ollama serve
In another:
  ollama pull nomic-embed-text
  ollama pull llama3.2:1b
  uv sync --locked
  uv run uvicorn app:app --host 127.0.0.1 --port 8000
Open http://127.0.0.1:8000 . Upload a document, wait for indexing, then ask a question. Click numbered source links to inspect extracted passages.

Model downloads require internet once. After downloads, inference and document processing run locally. Keep OLLAMA_NO_CLOUD=1 on the Ollama server and use downloaded local models only. The app connects directly to 127.0.0.1:11434, bypassing HTTP proxies.

Configuration
-------------
EMBED_MODEL: nomic-embed-text by default.
CHAT_MODEL: llama3.2:1b by default. Larger local models usually follow citation instructions better but need more RAM/VRAM.
DATA_DIR: ./data beside app.py by default; contains index.sqlite3 with extracted document text and vectors. Keep it private. It is not encrypted. Back it up while the app is stopped.
Example:
  CHAT_MODEL=llama3.2:3b uv run uvicorn app:app --host 127.0.0.1 --port 8000
Pull any chosen model before use. Delete all indexed documents before changing EMBED_MODEL, then upload again. Do not replace an embedding model's weights behind the same tag while using an existing index.

Behavior and limits
-------------------
- Text-based PDF, DOCX paragraphs/tables, and UTF-8 TXT. No OCR, image analysis, legacy .doc, or encrypted PDFs.
- Maximum upload: 20 MiB; maximum extracted text: 500,000 characters; maximum PDF length: 500 pages; maximum 600 passages per document. DOCX uncompressed content is limited to 50 MiB.
- PDF citations refer to original page numbers. DOCX and TXT use page 1 because stable printed pagination is unavailable.
- Overlapping 1,200-character passages, local embeddings, cosine similarity and top-five retrieval. Entire corpus vectors are scanned in memory: intended for small personal libraries, not large collections.
- Generated answers may omit inline citations or hallucinate. Retrieved-passage links always show the actual text supplied to the model, not a guarantee that it supports every generated claim. Verify sources. Retrieval scores are not confidence probabilities.
- Questions are independent, not a persistent conversation. Answer history and original uploaded files are not saved by the app. Extracted text and vectors persist until deleted.
- Deletion removes a document from active retrieval, not forensic erasure of SQLite free pages, operating-system caches or backups.
- Indexing and answer generation serialize within one process. Run one worker. Local inference can take minutes on CPU; requests time out after 180 seconds.
- Loopback-only personal app, no authentication. Do not expose it via a reverse proxy, public bind address or shared network. Host/origin checks reduce browser-based cross-site access, but this is not a hardened hostile-file service. Only upload trusted documents.
- Document instructions are treated as untrusted evidence in the prompt; prompt injection resistance is not guaranteed.

Troubleshooting
---------------
Model request failed: start Ollama, check its logs, and pull both configured models. Port 11434 must be reachable locally. If the web port is occupied, use --port 8001 and open the matching URL.
No readable text: run OCR externally or export the document as text before upload.
Embedding model mismatch: delete all documents through the library, choose the model, restart the app, then re-upload.

Verification
------------
  uv run python -m unittest -v
Regression tests cover persisted evidence, deletion, ingestion rollback, embedding-model changes, DOCX tables and unreadable files. They use deterministic model substitutes; real local-model and browser smoke checks are separate.

Private data, virtual environments and environment files are excluded from Git. Do not commit documents, model files, keys or the data directory.
