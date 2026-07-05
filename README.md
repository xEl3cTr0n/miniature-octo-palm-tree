# ClaimLens

ClaimLens is a portfolio-ready scaffold for a multimodal AI evidence intelligence platform. It is designed for insurance, legal, compliance, and operations workflows where reviewers need to reason over PDFs, images, audio, video, and structured case data.

## Why This Project Is Worth Building

For an MIS major transitioning into a more technical role, this is a strong project because it bridges business systems thinking with hands-on AI engineering. The domain rewards understanding workflows, controls, data quality, auditability, and stakeholder needs while still requiring technical depth in APIs, retrieval, evaluation, databases, and deployment.

The project demonstrates skills that map well to AI engineer, applied AI engineer, data/AI analyst, full-stack AI engineer, and technical product-adjacent roles:

- Multimodal ingestion for documents, images, audio, video, and tabular evidence.
- Retrieval-augmented generation with citations and confidence scoring.
- Agentic workflows for retrieval, policy comparison, contradiction checks, and report generation.
- Evaluation harnesses for citation coverage, retrieval quality, and hallucination prevention.
- Production patterns such as async processing, observability, typed schemas, CI, and deployment docs.

## Current Implementation

This repository starts with a deterministic Python/FastAPI core that can be expanded into the full system:

- `claimlens/core/ingestion.py` detects evidence types and chunks evidence for retrieval.
- `claimlens/core/retrieval.py` provides a stable retrieval interface backed by a simple lexical retriever.
- `claimlens/agents/checklists.py` checks missing evidence requirements for claim workflows.
- `claimlens/evaluators/faithfulness.py` provides a CI-friendly citation coverage metric.
- `claimlens/api/main.py` exposes health and question-answering endpoints.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
uvicorn claimlens.api.main:app --reload
```

## Example API Request

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "claim_type": "auto_collision",
    "question": "Is rear bumper damage supported?",
    "evidence": [
      {
        "id": "note-1",
        "type": "text",
        "title": "Adjuster Note",
        "content": "Rear bumper damage is visible in the uploaded photo and repair estimate."
      }
    ]
  }'
```

## Real Data Demo: NHTSA

ClaimLens can pull public vehicle complaint and recall data from NHTSA and convert it into citable evidence records.

Run a live terminal demo:

```bash
python scripts/import_nhtsa_case.py \
  --make Honda \
  --model Accord \
  --year 2020 \
  --question "Do complaints or recalls mention warning lights or rear camera failure?"
```

Or query it through the FastAPI app:

```bash
curl -X POST http://127.0.0.1:8000/ask/nhtsa \
  -H 'Content-Type: application/json' \
  -d '{
    "make": "Honda",
    "model": "Accord",
    "year": 2020,
    "question": "Do complaints or recalls mention warning lights or rear camera failure?",
    "max_complaints": 10,
    "max_recalls": 5
  }'
```

This source is useful for portfolio demos because it shows real-world data ingestion, evidence normalization, citation-backed retrieval, and review-oriented answers without requiring private claims data.

## Roadmap

1. Replace lexical retrieval with hybrid search using pgvector, BM25, metadata filters, and reranking.
2. Add OCR, ASR, image captioning, object detection, and video frame extraction adapters.
3. Add LangGraph agents for evidence retrieval, policy comparison, contradiction detection, and report generation.
4. Add golden datasets and evaluation dashboards for retrieval recall, citation precision, faithfulness, cost, and latency.
5. Add a reviewer UI with document preview, image regions, timestamps, graph visualization, and human feedback.
