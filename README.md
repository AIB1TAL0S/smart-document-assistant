# Smart Document Assistant

Ask questions about your PDF, DOCX and TXT files through a browser GUI. The app extracts text, creates local embeddings, retrieves relevant passages from a persistent SQLite index, and uses Ollama to generate an answer.

**Local inference. No cloud API key. Clickable retrieved sources.**

> This is a personal, loopback-only app, not a public hosted service. AI answers can be wrong: verify the retrieved passages before relying on them.

## Requirements

- [Git](https://git-scm.com/downloads)
- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python dependencies
- [Ollama](https://ollama.com/download) for local embeddings and answers
- Internet access for initial dependency and model downloads; enough free disk space for both models and your index

The default models are `nomic-embed-text` for embeddings and `llama3.2:1b` for answers. GPU acceleration is optional; CPU inference can be slow.

## Quick start

### 1. Get the project

```sh
git clone https://github.com/AIB1TAL0S/smart-document-assistant.git
cd smart-document-assistant
uv sync --locked
```

### 2. Start Ollama with cloud features disabled

In a separate terminal on Linux or macOS:

```sh
OLLAMA_NO_CLOUD=1 ollama serve
```

On Windows PowerShell:

```powershell
$env:OLLAMA_NO_CLOUD = "1"
ollama serve
```

Leave this terminal running. If Ollama is already running as an app or service, do not start a second instance. Configure `OLLAMA_NO_CLOUD=1` in that app/service's environment and restart it instead. Setting the variable in another terminal does not reconfigure an existing server.

### 3. Download the local models

Back in your project terminal:

```sh
ollama pull nomic-embed-text
ollama pull llama3.2:1b
ollama list
```

Both models should appear in the list. Downloads need internet once; document processing uses the local Ollama server at `127.0.0.1:11434`, bypassing HTTP proxies. Use downloaded local models, not cloud models.

### 4. Launch the GUI

```sh
uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in a browser on the same computer. Keep the app terminal running. This is a browser-based GUI, not a separate desktop executable.

## Using the GUI

1. Under **Add your documents**, choose a PDF, DOCX or TXT file.
2. Click **Index document**. Wait for extraction and local embedding generation to finish. The file appears in **Your library** with its passage count.
3. Enter a question in **What would you like to know?**, then click **Ask documents**.
4. Read the answer and click a numbered link under **Retrieved passages** to jump to its source excerpt. Inline citations are clickable when the model includes them.
5. Upload more files to search across your library. Each question retrieves from all indexed documents; there is no individual-document selection.
6. Click **Delete** next to a document and confirm to remove its indexed text from future retrieval.

Example questions:

- “What is the cancellation policy?”
- “Who owns this project, and what is the approved budget?”
- “Which deadlines are mentioned in these documents?”

Questions are independent: the app does not maintain a conversation or save answer history. It retrieves up to five passages per question, so broad requests such as “summarize every detail” may miss material. Source links show the actual passages supplied to the model; they do not guarantee every generated claim is supported.

### Stop and restart

Press `Ctrl+C` in the app terminal to stop the web server. Stop a manually launched Ollama server in its own terminal if you no longer need it.

To return later, start Ollama if needed and run the same `uv run uvicorn ...` command from the project directory. You do not need to download the models again. The document library survives restarts.

## Supported documents and limits

| Item | Support or limit |
| --- | --- |
| PDF | Text-based PDFs, with original page numbers in sources |
| DOCX | Paragraphs and tables; sources use page 1 because printed pagination is unavailable |
| TXT | UTF-8 text; sources use page 1 |
| Upload size | 20 MiB per file |
| Extracted text | 500,000 characters per document |
| PDF length | 500 pages |
| Indexed passages | 600 per document |
| DOCX expanded content | 50 MiB |
| Question length | 4,000 characters |

Scanned PDFs need OCR outside this app before upload. Images, legacy `.doc` files and encrypted PDFs are not supported. Upload trusted documents only; this is not a hardened hostile-file processing service.

## Configuration

Set environment variables **before starting the web app**:

| Variable | Default | Purpose |
| --- | --- | --- |
| `CHAT_MODEL` | `llama3.2:1b` | Local answer model |
| `EMBED_MODEL` | `nomic-embed-text` | Local embedding model |
| `DATA_DIR` | `data/` beside `app.py` | Folder containing the persistent `index.sqlite3` |

For a larger answer model on Linux or macOS:

```sh
ollama pull llama3.2:3b
CHAT_MODEL=llama3.2:3b uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

PowerShell equivalent:

```powershell
ollama pull llama3.2:3b
$env:CHAT_MODEL = "llama3.2:3b"
uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

Larger models generally need more RAM/VRAM and may follow citation instructions better. Pull the selected model before use.

**Changing embeddings:** delete all documents from the library, stop the app, set `EMBED_MODEL`, pull that model, restart, and upload the documents again. Existing vectors cannot be mixed with a different embedding model. Do not replace a model's weights behind the same tag while retaining an index built with the old weights.

Run a single web worker. Indexing and answer generation serialize within the process. Ollama HTTP requests time out after 180 seconds; a multi-batch upload may take longer overall.

## Privacy and storage

- The app saves extracted text and embedding vectors in SQLite, not original uploaded files.
- The database is **not encrypted**. Keep its directory private; stop the app before backing it up.
- Deletion removes a document from active retrieval. It is not forensic erasure of SQLite free pages, OS caches or backups.
- `data/`, virtual environments and environment files are excluded from Git. A custom `DATA_DIR` inside the repository may need an additional ignore rule. Never commit documents, databases, model files or credentials.
- The app has no authentication. Keep the `127.0.0.1` bind address; do not expose it using a public bind address, reverse proxy or tunnel.
- Host and origin checks reduce browser-based cross-site access. They are not a substitute for authentication or hardened deployment.
- Document text is treated as untrusted evidence in the model prompt, but prompt-injection resistance is not guaranteed.

Making this source repository public does **not** publish your local document library or host the application online.

## How RAG works here

```text
Upload → extract text → overlapping passages → local embeddings → SQLite
Question → local embedding → cosine search → top five passages → local answer
```

Passages are up to 1,200 characters with overlap. Retrieval scans the saved vectors in memory, so this is intended for small personal libraries rather than large collections. Similarity scores are not confidence probabilities.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Browser cannot connect | Keep the web-server terminal open and use the exact localhost address and port it prints. |
| Port 8000 is occupied | Start with `--port 8001`, then open `http://127.0.0.1:8001`. |
| Ollama port 11434 is occupied | An Ollama instance may already be running. Use/configure that instance rather than launching another. |
| Local Ollama request failed | Check Ollama logs, confirm it is running locally, and use `ollama list` to check both configured models are installed. |
| No readable text | Run OCR externally for scanned PDFs, or export the file as supported text. |
| Embedding model mismatch | Delete all documents, restart with the selected embedding model, and re-upload. |
| Answer is incomplete or wrong | Ask a narrower question, inspect source passages, and consider a larger downloaded chat model. |
| Model omits inline citations | Use the separate **Retrieved passages** links; do not assume unlinked claims are supported. |

## Development checks

```sh
uv run python -m unittest -v
```

Regression tests cover persisted evidence and deletion, ingestion rollback, embedding-model changes, DOCX tables, and unreadable files. They use deterministic model substitutes; they do not prove live model quality.

For a real smoke check, launch the app with Ollama, upload a document containing a known fact, ask about that fact, inspect its source excerpt, restart the app to check persistence, then delete the document.

### Project layout

- `app.py` — FastAPI routes, local request checks and GUI entry point
- `engine.py` — extraction, embeddings, SQLite index, retrieval and answers
- `static/index.html` — browser GUI; no external frontend assets
- `test_engine.py` — regression tests
- `pyproject.toml`, `uv.lock` — Python dependencies and lockfile
- `PLAN.txt` — initial implementation plan
