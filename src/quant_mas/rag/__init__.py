"""Retrieval augmented generation package."""

from quant_mas.rag.document_loader import Document, load_document, load_documents
from quant_mas.rag.simple_retriever import RetrievalResult, SimpleRetriever

__all__ = [
    "Document",
    "RetrievalResult",
    "SimpleRetriever",
    "load_document",
    "load_documents",
]
