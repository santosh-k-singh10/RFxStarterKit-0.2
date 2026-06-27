"""
core/embedder.py
----------------
Builds a FAISS vector index from document chunks and provides a retrieval
method used by the synthesizer to verify that extracted requirements are
actually grounded in the source text.

If sentence-transformers or faiss are not installed, verification is skipped
gracefully and confidence scores remain unchanged.
"""

from __future__ import annotations

import structlog
from core.schemas import DocumentChunk, Requirement

log = structlog.get_logger()

_EMBED_MODEL = "all-MiniLM-L6-v2"   # 80MB, fast, good for English text
_VERIFY_THRESHOLD = 0.35             # cosine similarity below this → flag as ungrounded


class DocumentIndex:
    """
    Thin wrapper around a FAISS flat index.
    Build once after ingestion; query per requirement during synthesis.
    """

    def __init__(self, chunks: list[DocumentChunk]):
        self._available = False
        self._chunks = chunks

        try:
            import faiss                                    # noqa: F401
            from sentence_transformers import SentenceTransformer  # noqa: F401
            self._model = SentenceTransformer(_EMBED_MODEL)
            self._build_index(chunks)
            self._available = True
            log.info("vector_index_built", chunks=len(chunks))
        except ImportError:
            log.warning("embedder_unavailable_skipping_rag_verification")

    def _build_index(self, chunks: list[DocumentChunk]) -> None:
        import faiss
        import numpy as np

        texts = [c.text for c in chunks]
        embeddings = self._model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        # Normalise for cosine similarity via inner product
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(embeddings)
        self._texts = texts

    def verify_requirement(self, req: Requirement) -> float:
        """
        Return the best cosine similarity between the requirement description
        and any chunk in the document. Values near 1.0 = well-grounded.
        """
        if not self._available:
            return 1.0  # Can't verify → don't penalise

        import faiss
        import numpy as np

        query = self._model.encode([req.description], show_progress_bar=False)
        query = np.array(query).astype("float32")
        faiss.normalize_L2(query)

        scores, _ = self._index.search(query, k=1)
        return float(scores[0][0])

    def flag_ungrounded(self, requirements: list[Requirement]) -> list[Requirement]:
        """
        For each requirement, check retrieval score.
        If below threshold, lower confidence and set ambiguity_flag.
        Returns the modified list.
        """
        if not self._available:
            return requirements

        for req in requirements:
            score = self.verify_requirement(req)
            if score < _VERIFY_THRESHOLD:
                req.confidence = min(req.confidence, score)
                req.ambiguity_flag = True
                if not req.clarification_question:
                    req.clarification_question = (
                        f"This requirement could not be directly traced back to "
                        f"source text (retrieval score {score:.2f}). "
                        f"Please confirm it is present in the RFP."
                    )
                log.debug("ungrounded_requirement", id=req.id, score=score)

        return requirements
