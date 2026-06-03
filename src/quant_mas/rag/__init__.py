"""Retrieval augmented generation package."""

from quant_mas.rag.chunking import chunk_text
from quant_mas.rag.document_loader import Document, load_document, load_documents
from quant_mas.rag.embedding_client import (
    EmbeddingClient,
    HashEmbeddingClient,
    OpenAICompatibleEmbeddingClient,
)
from quant_mas.rag.hybrid_retriever import HybridRetrievalResult, HybridRetriever
from quant_mas.rag.in_memory_vector_store import InMemoryVectorStore
from quant_mas.rag.simple_retriever import RetrievalResult, SimpleRetriever
from quant_mas.rag.vector_store_base import VectorSearchResult, VectorStore
from quant_mas.rag.vector_store_pgvector import PgVectorStore

__all__ = [
    "Document",
    "EmbeddingClient",
    "HashEmbeddingClient",
    "HybridRetrievalResult",
    "HybridRetriever",
    "InMemoryVectorStore",
    "OpenAICompatibleEmbeddingClient",
    "PgVectorStore",
    "RetrievalResult",
    "SimpleRetriever",
    "VectorSearchResult",
    "VectorStore",
    "chunk_text",
    "load_document",
    "load_documents",
]
