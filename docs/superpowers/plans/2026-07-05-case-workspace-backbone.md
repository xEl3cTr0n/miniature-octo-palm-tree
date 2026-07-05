# Case Workspace Backbone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first product backbone for ClaimLens: persistent-in-process case records, reviewer questions, reports, and NHTSA case import through stable API endpoints.

**Architecture:** Keep the current deterministic v2 package. Add a small `claimlens.core.cases` module that owns case IDs, summaries, reports, and an in-memory `CaseStore`; expose it from `claimlens.api.main` without adding external infrastructure yet. The store is intentionally swappable for SQLite/Postgres later.

**Tech Stack:** Python 3.11, FastAPI, Pydantic request models, dataclass domain models, pytest, FastAPI TestClient.

---

### Task 1: Case Domain Module

**Files:**
- Create: `claimlens/core/cases.py`
- Test: `tests/test_cases.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_cases.py` with tests for creating a case, listing a summary, asking a stored case question, and generating a report with citations.

- [ ] **Step 2: Run failing tests**

Run: `.venv/bin/python -m pytest tests/test_cases.py -q`
Expected: FAIL because `claimlens.core.cases` does not exist.

- [ ] **Step 3: Implement `CaseStore` and report helpers**

Add focused dataclasses: `CaseRecord`, `CaseSummary`, `CaseReport`, and `CaseStore`. Store records in memory and call `answer_claim` for question/report logic.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_cases.py -q`
Expected: PASS.

### Task 2: Case API Endpoints

**Files:**
- Modify: `claimlens/api/main.py`
- Test: `tests/test_api_cases.py`

- [ ] **Step 1: Write failing API tests**

Test `POST /cases`, `GET /cases`, `POST /cases/{case_id}/ask`, `GET /cases/{case_id}/report`, and `POST /cases/import/nhtsa` with the NHTSA fetch mocked.

- [ ] **Step 2: Run failing tests**

Run: `.venv/bin/python -m pytest tests/test_api_cases.py -q`
Expected: FAIL because endpoints are missing.

- [ ] **Step 3: Implement endpoints**

Add request models in `claimlens/api/main.py`, instantiate one module-level `CaseStore`, and wire endpoints to the store. Keep existing `/ask`, `/ask/nhtsa`, and `/data-sources/nhtsa/vehicle-evidence` working.

- [ ] **Step 4: Run API tests**

Run: `.venv/bin/python -m pytest tests/test_api_cases.py -q`
Expected: PASS.

### Task 3: Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/roadmap.md`

- [ ] **Step 1: Update docs**

Add the case workspace API flow and NHTSA import flow to README. Update roadmap Phase 1.5 to name case workspace endpoints.

- [ ] **Step 2: Full verification**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 3: Gas Town and Git loop**

Commit from `/private/tmp/claimlens-gastown/claimlens/crew/codex`, push to `origin/main`, then update the Gas Town convoy/hook state for `hq-cv-qhv21` / `hq-hak`.
