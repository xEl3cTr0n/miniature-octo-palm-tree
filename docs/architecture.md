# ClaimLens Architecture

## System Overview

ClaimLens turns mixed case evidence into cited, reviewable AI outputs. The production architecture separates ingestion, retrieval, orchestration, evaluation, and review UI concerns.

```text
Next.js Review UI
  -> FastAPI Case API
    -> Ingestion Queue
      -> OCR / ASR / Vision / Text Parsers
    -> Retrieval Service
      -> pgvector + BM25 + reranker + metadata filters
    -> Agent Orchestrator
      -> retrieval agent
      -> policy agent
      -> contradiction agent
      -> missing evidence agent
      -> report agent
    -> Evaluation Service
      -> citation precision
      -> retrieval recall
      -> answer faithfulness
      -> latency and cost tracking
```

## Hugging Face Task Mapping

The intended full build uses these task families:

- Document question answering for forms, policies, and reports.
- Visual document retrieval for scanned pages, tables, and signatures.
- Image-text-to-text and visual question answering for photos and screenshots.
- Automatic speech recognition for recorded statements and calls.
- Object detection and image segmentation for visual evidence regions.
- Feature extraction and sentence similarity for embeddings.
- Text classification, token classification, summarization, text ranking, and question answering for case reasoning.

## Portfolio Differentiators

The project is intentionally scoped beyond a basic chatbot. It should show:

- grounded answers with citations;
- multimodal evidence retrieval;
- human-reviewable confidence and missing-evidence flags;
- deterministic tests and offline evals;
- clean separation between prototype logic and production adapters.
