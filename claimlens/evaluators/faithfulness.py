from __future__ import annotations

from claimlens.core.retrieval import tokenize


def citation_coverage(answer: str, cited_contexts: list[str]) -> float:
    """Estimate whether answer terms are grounded in cited evidence.

    This intentionally simple metric is deterministic for CI. Production evals
    should add RAGAS/DeepEval-style faithfulness, answer relevance, and human
    review labels.
    """
    answer_terms = set(tokenize(answer))
    if not answer_terms:
        return 1.0
    context_terms = set(tokenize(" ".join(cited_contexts)))
    return round(len(answer_terms & context_terms) / len(answer_terms), 3)
