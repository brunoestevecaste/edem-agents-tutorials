# Local RAG Agent

A minimal local RAG tutorial: download a PDF from a URL, build a FAISS index in a notebook, then query it from an ADK agent using ADK's `LlamaIndexRetrieval` tool.

## Concepts

- Local vector search with FAISS
- PDF downloading, text extraction, chunking, embedding, and index persistence
- ADK retrieval tools with `LlamaIndexRetrieval`
- Shared model configuration via `src/tutorials/model_config.py`
- Separating indexing time from agent runtime

## Setup

```bash
uv sync --extra adk --extra notebooks --extra rag
```

### Option A: Gemini (default)

Gemini is used for both the agent model and the embedding model in this tutorial.

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

If you edit `.env` while the notebook is already running, rerun the first notebook cell before building the index.

### Option B: Groq for the agent, Gemini for embeddings

The agent can use Groq, but the local FAISS index still uses Gemini embeddings.

```bash
export MODEL_PROVIDER=groq
export GROQ_API_KEY="your-groq-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Option C: Vertex AI for both the agent and embeddings

One-time auth on your machine:

```bash
gcloud auth application-default login
```

Then configure the provider:

```bash
export MODEL_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="global"
# optional
export VERTEX_MODEL="gemini-2.5-flash-lite"
```

In Vertex mode, the notebook and agent use `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and Application Default Credentials for embeddings too. No Gemini API key is needed. The LLM and embedding model are both created through `src/tutorials/model_config.py`.

## 1. Build The Local Index

Choose a PDF URL. The notebook defaults to the Agencia Tributaria Renta 2025 manual:

```bash
export LOCAL_RAG_PDF_URL="https://sede.agenciatributaria.gob.es/static_files/Sede/Biblioteca/Manual/Practicos/IRPF/IRPF-2025/ManualRenta2025Parte1_es_es.pdf"
```

The default run indexes the first 25 PDF pages to keep the classroom example quick. Set `LOCAL_RAG_MAX_PAGES=0` to process the full PDF.

Run the notebook from the repository root:

```bash
uv run jupyter notebook notebooks/local_rag_indexing.ipynb
```

The notebook downloads the PDF to `src/tutorials/t09_local_rag_agent/downloads/`, creates chunks, embeds them, and persists a FAISS index to `src/tutorials/t09_local_rag_agent/storage/`.

## 2. Run The Agent

After the index exists:

```bash
uv run adk web src/tutorials/t09_local_rag_agent
```

Open [http://localhost:8000](http://localhost:8000), pick **local_rag**, and try:

- "Qué novedades principales incluye el manual?"
- "Qué indica el manual sobre el mínimo personal y familiar?"
- "Resume lo que dice el PDF sobre rendimientos del trabajo"
- "Dónde aparece información sobre deducciones?"

## Notes

The downloaded PDFs and FAISS index are generated locally and ignored by git. If you change `LOCAL_RAG_PDF_URL` or `LOCAL_RAG_MAX_PAGES`, rerun `notebooks/local_rag_indexing.ipynb` before starting the agent again.
