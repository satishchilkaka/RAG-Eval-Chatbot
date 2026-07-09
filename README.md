# RAG Eval Project

A document Q&A chatbot built with **FastAPI** (Python) and **React + TypeScript**. Upload documents, index them with local embeddings, and ask questions answered via **Groq's** free, OpenAI-compatible API (swap in any other OpenAI-compatible provider by changing `LLM_BASE_URL`).

## Architecture

```
Upload (PDF/TXT/DOCX/MD) → Chunk → Embed (sentence-transformers) → ChromaDB
                                                                          ↓
User Question → Retrieve top-k chunks → LLM (Groq, OpenAI-compatible) → Answer + Sources
```

## Quick Start (Docker — recommended)

### 1. Configure API key

Edit `.env` in the project root and set your Groq key:

```env
LLM_API_KEY=gsk_your-key-here
```

Get a free key (no credit card required) at [console.groq.com/keys](https://console.groq.com/keys). The free tier covers Llama 3.3 70B with generous rate limits.

Want a different provider? Any OpenAI-compatible API works — just change `LLM_BASE_URL` and `LLM_MODEL` in `.env` (e.g. Google Gemini, OpenRouter, or OpenAI itself).

### 2. Run everything with one command

```bash
cd rag-eval-project
docker compose up --build
```

Open **http://localhost:3080** — frontend and backend start together.

Other useful commands:

```bash
docker compose up -d --build   # run in background
docker compose down            # stop containers
docker compose logs -f         # view logs
```

The first build takes a few minutes (downloads ML dependencies). Uploaded documents and the vector store persist in `./data/`.

## Local development (without Docker)

### Backend

```bash
cd rag-eval-project/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd rag-eval-project/frontend
npm install
npm run dev
```

App: http://localhost:5173

## Deploying for testing (Render free tier)

This app persists uploaded documents and the vector index to local disk, so it needs a host that keeps a container running rather than pure serverless functions (Vercel's free functions are stateless between requests and would lose your indexed documents). Render's free tier works well for spinning up a live instance to run QA tests against.

A `render.yaml` blueprint is included, defining two services:

- **`rag-eval-backend`** — the FastAPI app, deployed from `backend/Dockerfile`.
- **`rag-eval-frontend`** — the React app, deployed as a free static site.

### Steps

1. Push this repo to GitHub.
2. In the Render dashboard: **New > Blueprint**, point it at the repo. Render reads `render.yaml` and creates both services.
3. On `rag-eval-backend`, set the `LLM_API_KEY` env var to your Groq key.
4. Once both services have deployed, copy each other's URL:
   - Set `rag-eval-backend`'s `EXTRA_CORS_ORIGINS` env var to the frontend's URL (e.g. `https://rag-eval-frontend.onrender.com`), then redeploy the backend.
   - Set `rag-eval-frontend`'s `VITE_API_URL` env var to the backend's URL (e.g. `https://rag-eval-backend.onrender.com`), then trigger a manual redeploy of the frontend (static sites need a rebuild to pick up env changes).
5. Open the frontend URL.

**Caveats for a free-tier deploy:**

- Free web services spin down after 15 minutes idle; the first request after that takes 30–60s to wake up.
- Storage is not persistent across redeploys or restarts — uploaded documents and the vector index reset when the backend service restarts. Fine for an active testing session; not for long-term storage.
- If you need durable storage or no spin-down, that's a paid Render plan (persistent disks require a paid instance type).

## Supported file types

- PDF (`.pdf`)
- Word (`.docx`)
- Plain text (`.txt`, `.md`, `.csv`)

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/documents` | List indexed documents |
| POST | `/api/documents/upload` | Upload & index a file |
| DELETE | `/api/documents/{id}` | Remove a document |
| POST | `/api/chat` | Ask a question |

## Configuration

All settings live in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | — | Your API key for the LLM provider |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Base URL of an OpenAI-compatible API |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | LLM model |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `4` | Chunks retrieved per question |

## Project structure

```
rag-eval-project/
├── .env                  # API keys & config
├── docker-compose.yml    # One-command startup
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py       # FastAPI app
│   │   ├── routers/      # API routes
│   │   └── services/     # RAG, embeddings, LLM
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf        # Proxies /api → backend
│   └── src/
│       ├── components/   # Upload, chat, doc list
│       └── api/          # API client
└── data/
    ├── uploads/          # Uploaded files
    └── chroma/           # Vector store
```
