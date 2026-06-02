"""Optional FAISS vector store placeholder."""

from __future__ import annotations


class FaissVectorStore:
    """Placeholder for future FAISS integration."""

    def __init__(self, *args, **kwargs) -> None:
        try:
            import faiss  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "FaissVectorStore requires faiss. Install faiss before using "
                "vector_store=faiss."
            ) from exc
        raise NotImplementedError("FAISS backend is reserved for a future Quant MAS release")
