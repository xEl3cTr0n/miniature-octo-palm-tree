from __future__ import annotations

import math
import re
from collections import Counter

from claimlens.core.models import EvidenceChunk, RetrievalHit

_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9$]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_PATTERN.findall(text)]


class HybridRetriever:
    """Small lexical retriever that mirrors the production retrieval contract.

    The roadmap upgrades this with pgvector embeddings, BM25, metadata filters,
    visual retrieval, and reranking while keeping the query interface stable.
    """

    def __init__(self, chunks: list[EvidenceChunk]) -> None:
        self._chunks = chunks
        self._chunk_terms = [Counter(tokenize(chunk.text)) for chunk in chunks]
        self._doc_freq = Counter(
            token for terms in self._chunk_terms for token in terms.keys()
        )

    def search(self, query: str, *, limit: int = 5) -> list[RetrievalHit]:
        query_terms = Counter(tokenize(query))
        if not query_terms:
            return []

        hits: list[RetrievalHit] = []
        total_chunks = max(len(self._chunks), 1)
        for chunk, terms in zip(self._chunks, self._chunk_terms, strict=True):
            score = 0.0
            for token, query_weight in query_terms.items():
                if token not in terms:
                    continue
                idf = math.log((1 + total_chunks) / (1 + self._doc_freq[token])) + 1
                score += query_weight * terms[token] * idf
            if score > 0:
                hits.append(RetrievalHit(chunk=chunk, score=round(score, 4)))

        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]
