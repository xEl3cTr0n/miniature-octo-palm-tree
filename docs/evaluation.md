# Evaluation Strategy

ClaimLens should be evaluated like a real AI system, not only like a demo chatbot.

## Metrics

- **Retrieval recall:** percentage of golden supporting evidence retrieved in the top-k results.
- **Citation precision:** percentage of cited snippets that directly support the generated answer.
- **Faithfulness:** percentage of generated claims that are grounded in retrieved evidence.
- **Contradiction precision:** percentage of contradiction findings that represent a real mismatch.
- **Missing-evidence accuracy:** percentage of required checklist items correctly marked present or missing.
- **Latency:** time from user query to grounded answer.
- **Cost per case:** model and infrastructure cost to process one evidence packet.

## Golden dataset plan

Create 20-50 synthetic case packets with known answers, required artifacts, contradictions, and expected citations. Include clean cases, ambiguous cases, conflicting cases, and incomplete cases.
