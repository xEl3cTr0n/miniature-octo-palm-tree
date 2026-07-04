# ClaimLens

A multimodal AI evidence intelligence platform for insurance, legal, and compliance case review.

ClaimLens is designed as a portfolio-grade AI engineering project: it ingests mixed evidence packets, creates structured evidence records, performs citation-grounded retrieval, flags contradictions and missing evidence, and produces reviewer-ready reports.

## Why this project is valuable for an MIS-to-technical transition

This project is a strong bridge from MIS into technical AI/software roles because it combines business-process analysis with production engineering:

- **Business workflow modeling:** claim review, evidence intake, compliance checklists, and audit reporting.
- **Data systems:** normalized metadata, vector-ready evidence chunks, schemas, and reproducible datasets.
- **Backend engineering:** FastAPI services, typed models, testable pipelines, and API contracts.
- **Applied AI:** multimodal task routing, retrieval-augmented generation design, evaluation, and human review loops.
- **LLMOps:** measurable faithfulness, citation quality, latency, and reviewer feedback.

## MVP included in this repo

This initial build includes a runnable backend-oriented foundation:

- A FastAPI app with endpoints for health checks, case ingestion, querying, contradiction detection, missing-evidence checks, and report generation.
- A deterministic local evidence pipeline that can run without paid model APIs.
- Domain schemas for cases, evidence items, citations, findings, and reports.
- A synthetic claim packet for demo/testing.
- Unit tests covering ingestion, retrieval, contradiction detection, and missing-evidence logic.
- Documentation for architecture, roadmap, and evaluation strategy.

## Hugging Face task mapping

ClaimLens is designed to integrate these Hugging Face task families:

- Document Question Answering
- Visual Document Retrieval
- Image-Text-to-Text
- Visual Question Answering
- Automatic Speech Recognition
- Feature Extraction
- Question Answering
- Sentence Similarity
- Summarization
- Text Classification
- Text Ranking
- Token Classification
- Object Detection
- Image Segmentation

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn claimlens_api.main:app --reload
```

Run tests:

```bash
pytest
```

Try the demo:

```bash
python scripts/demo_case.py
```
