# ClaimLens Architecture

## Goal

ClaimLens demonstrates a production-minded multimodal AI workflow for claim, legal, and compliance review. The system starts with deterministic local components and is structured so Hugging Face models can replace each placeholder processor as the project matures.

## Pipeline

1. **Evidence ingestion** accepts documents, images, audio, video, email, and structured records.
2. **Task routing** maps each artifact to model families such as document question answering, visual document retrieval, image-text-to-text, automatic speech recognition, text classification, and summarization.
3. **Evidence normalization** converts model outputs into typed `EvidenceItem` records.
4. **Retrieval** ranks evidence against reviewer questions and returns citations.
5. **Reasoning checks** flag contradictions and missing evidence.
6. **Report generation** produces reviewer next steps with grounded citations.

## Production extension points

- Replace keyword retrieval with pgvector hybrid search and a reranker.
- Persist cases in PostgreSQL instead of the in-memory demo store.
- Add object storage for source files.
- Add LangGraph agents for ingestion, retrieval, policy comparison, contradiction detection, evaluation, and report writing.
- Add tracing with OpenTelemetry, Phoenix, or LangSmith.
