"""Local RAG ADK agent backed by a persisted FAISS index."""

import os
from pathlib import Path

from google.adk import Agent
from google.adk.tools.retrieval import LlamaIndexRetrieval
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore

try:
    from tutorials.model_config import get_embedding_model, get_model
except ModuleNotFoundError:
    import importlib
    import sys

    tutorials_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(tutorials_dir))
    _model_config = importlib.import_module("model_config")
    get_embedding_model = _model_config.get_embedding_model
    get_model = _model_config.get_model

TUTORIAL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_STORAGE_DIR = TUTORIAL_DIR / "storage"


def _load_env_file() -> None:
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _storage_dir() -> Path:
    storage_dir = Path(
        os.getenv("LOCAL_RAG_STORAGE_DIR", str(DEFAULT_STORAGE_DIR))
    ).expanduser()
    if not storage_dir.is_absolute():
        storage_dir = REPO_ROOT / storage_dir
    return storage_dir


def _load_retriever():
    _load_env_file()
    storage_dir = _storage_dir()
    if not storage_dir.exists():
        raise RuntimeError(
            "Local RAG index not found. Run notebooks/local_rag_indexing.ipynb "
            "before starting this agent."
        )

    embed_model =  get_embedding_model()
    vector_store = FaissVectorStore.from_persist_dir(str(storage_dir))
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=str(storage_dir),
    )
    index = load_index_from_storage(
        storage_context=storage_context,
        embed_model=embed_model,
    )
    return index.as_retriever(
        similarity_top_k=int(os.getenv("LOCAL_RAG_TOP_K", "3")),
    )


local_knowledge_tool = LlamaIndexRetrieval(
    name="search_local_knowledge_base",
    description=(
        "Retrieve relevant context from the local FAISS knowledge base for "
        "questions about the downloaded PDF."
    ),
    retriever=_load_retriever(),
)

root_agent = Agent(
    model=get_model(),
    name="local_rag_agent",
    description="Answers questions using a local FAISS-backed RAG index.",
    instruction=(
        "You answer questions using a local RAG knowledge base.\n"
        "Always call search_local_knowledge_base before answering questions about the downloaded PDF.\n"
        "Base your answer on the retrieved context, and keep it concise.\n"
        "If the retrieved context does not contain enough information, say that the local "
        "knowledge base does not contain enough information."
    ),
    tools=[local_knowledge_tool],
)
