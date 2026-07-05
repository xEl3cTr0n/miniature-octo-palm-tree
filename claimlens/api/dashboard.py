from __future__ import annotations


def render_dashboard() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ClaimLens</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7f9;
      --panel: #ffffff;
      --ink: #1d252d;
      --muted: #5e6b76;
      --line: #d8e0e7;
      --accent: #0f766e;
      --accent-strong: #0b5d56;
      --warn: #a16207;
      --danger: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      max-width: 1320px;
      margin: 0 auto;
      padding: 16px 20px;
    }
    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 22px; font-weight: 700; letter-spacing: 0; }
    h2 { font-size: 16px; font-weight: 700; letter-spacing: 0; }
    h3 { font-size: 14px; font-weight: 700; letter-spacing: 0; }
    .status {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--muted);
      font-size: 13px;
      background: #fbfcfd;
    }
    main {
      max-width: 1320px;
      margin: 0 auto;
      padding: 20px;
    }
    .workspace {
      display: grid;
      grid-template-columns: 340px minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 48px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      background: #fbfcfd;
    }
    .panel-body { padding: 14px; }
    .stack { display: grid; gap: 12px; }
    .field { display: grid; gap: 6px; }
    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }
    input, textarea {
      width: 100%;
      min-height: 38px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--ink);
      background: #fff;
      font: inherit;
      font-size: 14px;
    }
    textarea {
      min-height: 84px;
      resize: vertical;
      line-height: 1.4;
    }
    button {
      min-height: 38px;
      padding: 8px 12px;
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
    }
    button.secondary {
      border-color: var(--line);
      background: #fff;
      color: var(--ink);
    }
    button:disabled {
      cursor: not-allowed;
      opacity: .6;
    }
    .case-list {
      display: grid;
      gap: 8px;
    }
    .case-row {
      width: 100%;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      text-align: left;
    }
    .case-row.active {
      border-color: var(--accent);
      box-shadow: inset 3px 0 0 var(--accent);
    }
    .meta {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    .content-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 16px;
    }
    .result {
      min-height: 180px;
      white-space: pre-wrap;
      color: var(--ink);
      font-size: 14px;
      line-height: 1.5;
    }
    .citation {
      padding: 8px 10px;
      border-left: 3px solid var(--accent);
      background: #eef8f6;
      font-size: 13px;
      line-height: 1.4;
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }
    .metric {
      min-height: 72px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .metric strong {
      display: block;
      font-size: 20px;
      line-height: 1.2;
    }
    .metric span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }
    .eval-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .evidence-item {
      display: grid;
      gap: 6px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .evidence-snippet {
      color: var(--ink);
      font-size: 13px;
      line-height: 1.45;
    }
    .badge {
      min-width: 52px;
      padding: 4px 8px;
      border-radius: 6px;
      text-align: center;
      font-size: 12px;
      font-weight: 800;
    }
    .badge.pass {
      color: var(--accent-strong);
      background: #dff5ef;
    }
    .badge.fail {
      color: var(--danger);
      background: #fde8e6;
    }
    .empty {
      color: var(--muted);
      font-size: 14px;
    }
    .error { color: var(--danger); }
    .warn { color: var(--warn); }
    @media (max-width: 900px) {
      .workspace, .content-grid, .metrics-grid { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div>
        <h1>ClaimLens</h1>
        <p class="meta">Evidence review console</p>
      </div>
      <div class="status" id="status">Ready</div>
    </div>
  </header>
  <main>
    <div class="workspace">
      <section class="panel">
        <div class="panel-header">
          <h2>Import NHTSA Case</h2>
        </div>
        <div class="panel-body stack">
          <div class="field">
            <label for="make">Make</label>
            <input id="make" value="Honda" autocomplete="off">
          </div>
          <div class="field">
            <label for="model">Model</label>
            <input id="model" value="Accord" autocomplete="off">
          </div>
          <div class="field">
            <label for="year">Year</label>
            <input id="year" value="2020" inputmode="numeric">
          </div>
          <button id="importButton" type="button">Import Case</button>
          <button class="secondary" id="seedDemoButton" type="button">Seed Demo Case</button>
          <div class="panel-header" style="margin: 4px -14px -2px;">
            <h2>Manual Evidence Case</h2>
          </div>
          <div class="field">
            <label for="manualTitle">Case Title</label>
            <input id="manualTitle" value="Manual evidence review" autocomplete="off">
          </div>
          <div class="field">
            <label for="manualClaimType">Claim Type</label>
            <input id="manualClaimType" value="auto_collision" autocomplete="off">
          </div>
          <div class="field">
            <label for="manualEvidenceTitle">Evidence Title</label>
            <input id="manualEvidenceTitle" value="Adjuster note" autocomplete="off">
          </div>
          <div class="field">
            <label for="manualEvidenceContent">Evidence Text</label>
            <textarea id="manualEvidenceContent">Rear bumper damage is visible in the uploaded photo and repair estimate.</textarea>
          </div>
          <button id="manualCreateButton" type="button">Create Manual Case</button>
          <div class="panel-header" style="margin: 4px -14px -2px;">
            <h2>Case Queue</h2>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="secondary" id="refreshButton" type="button">Refresh</button>
              <button class="secondary" id="deleteCaseButton" type="button">Delete Case</button>
            </div>
          </div>
          <div class="case-list" id="caseList">
            <p class="empty">No cases loaded.</p>
          </div>
          <div class="panel-header" style="margin: 4px -14px -2px;">
            <h2>Case JSON Bundle</h2>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="secondary" id="exportBundleButton" type="button">Export JSON</button>
              <button class="secondary" id="importBundleButton" type="button">Import JSON</button>
            </div>
          </div>
          <div class="field">
            <label for="caseBundleJson">Bundle JSON</label>
            <textarea id="caseBundleJson" placeholder="Export a selected case or paste a ClaimLens case bundle."></textarea>
          </div>
        </div>
      </section>
      <section class="stack">
        <section class="panel">
          <div class="panel-header">
            <h2>Ask Reviewer Question</h2>
          </div>
          <div class="panel-body stack">
            <div class="field">
              <label for="question">Question</label>
              <textarea id="question">Does the evidence mention warning lights or rear camera failure?</textarea>
            </div>
            <button id="askButton" type="button">Ask Case</button>
            <div class="result" id="answer">
              <p class="empty">Select or import a case, then ask a question.</p>
            </div>
          </div>
        </section>
        <section class="content-grid">
          <section class="panel">
            <div class="panel-header">
              <h2>Reviewer Report</h2>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button class="secondary" id="reportButton" type="button">Generate</button>
                <button class="secondary" id="exportMarkdownButton" type="button">Export Markdown</button>
              </div>
            </div>
            <div class="panel-body result" id="report">
              <p class="empty">No report generated.</p>
            </div>
          </section>
          <section class="panel">
            <div class="panel-header">
              <h2>Citations</h2>
            </div>
            <div class="panel-body stack" id="citations">
              <p class="empty">No citations yet.</p>
            </div>
          </section>
        </section>
        <section class="panel">
          <div class="panel-header">
            <h2>Evidence Inspector</h2>
          </div>
          <div class="panel-body stack" id="caseEvidence">
            <p class="empty">No case selected.</p>
          </div>
        </section>
        <section class="panel">
          <div class="panel-header">
            <h2>Evaluation Metrics</h2>
            <button class="secondary" id="evalButton" type="button">Run Evals</button>
          </div>
          <div class="panel-body stack">
            <div class="metrics-grid" id="evalMetrics">
              <div class="metric">
                <strong>--</strong>
                <span>Pass rate</span>
              </div>
              <div class="metric">
                <strong>--</strong>
                <span>Citation coverage</span>
              </div>
              <div class="metric">
                <strong>--</strong>
                <span>Expected citation recall</span>
              </div>
            </div>
            <div class="stack" id="evalResults">
              <p class="empty">No evaluation run yet.</p>
            </div>
          </div>
        </section>
      </section>
    </div>
  </main>
  <script>
    let selectedCaseId = null;

    const statusEl = document.getElementById("status");
    const caseListEl = document.getElementById("caseList");
    const answerEl = document.getElementById("answer");
    const reportEl = document.getElementById("report");
    const citationsEl = document.getElementById("citations");
    const caseEvidenceEl = document.getElementById("caseEvidence");
    const evalMetricsEl = document.getElementById("evalMetrics");
    const evalResultsEl = document.getElementById("evalResults");
    const caseBundleJsonEl = document.getElementById("caseBundleJson");

    function setStatus(message, isError = false) {
      statusEl.textContent = message;
      statusEl.className = isError ? "status error" : "status";
    }

    async function requestJson(url, options = {}) {
      const response = await fetch(url, options);
      if (!response.ok) {
        const body = await response.text();
        throw new Error(body || `Request failed: ${response.status}`);
      }
      return response.json();
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function renderCitations(citations) {
      if (!citations || citations.length === 0) {
        citationsEl.innerHTML = '<p class="empty">No citations returned.</p>';
        return;
      }
      citationsEl.innerHTML = citations
        .map((citation) => `<div class="citation">${escapeHtml(citation)}</div>`)
        .join("");
    }

    function renderAnswer(payload) {
      answerEl.textContent = `${payload.answer}\\n\\nConfidence: ${payload.confidence}`;
      renderCitations(payload.citations);
    }

    function clearSelectedCasePanels() {
      answerEl.innerHTML = '<p class="empty">Select or import a case, then ask a question.</p>';
      reportEl.innerHTML = '<p class="empty">No report generated.</p>';
      citationsEl.innerHTML = '<p class="empty">No citations yet.</p>';
      caseEvidenceEl.innerHTML = '<p class="empty">No case selected.</p>';
    }

    function renderReport(payload) {
      reportEl.textContent = [
        payload.summary,
        "",
        `Evidence items: ${payload.evidence_count}`,
        `Confidence: ${payload.answer.confidence}`,
        "",
        "Next steps:",
        ...payload.next_steps.map((step) => `- ${step}`)
      ].join("\\n");
      renderCitations(payload.answer.citations);
    }

    function renderCaseEvidence(payload) {
      if (!payload.evidence || payload.evidence.length === 0) {
        caseEvidenceEl.innerHTML = '<p class="empty">No evidence attached.</p>';
        return;
      }
      caseEvidenceEl.innerHTML = payload.evidence.map((item) => {
        const metadata = Object.entries(item.metadata || {})
          .map(([key, value]) => `${escapeHtml(key)}: ${escapeHtml(value)}`)
          .join(" · ");
        const snippet = item.content.length > 320
          ? `${item.content.slice(0, 320)}...`
          : item.content;
        return `
          <div class="evidence-item">
            <div>
              <strong>${escapeHtml(item.title)}</strong>
              <div class="meta">${escapeHtml(item.type)}${metadata ? ` · ${metadata}` : ""}</div>
            </div>
            <div class="evidence-snippet">${escapeHtml(snippet)}</div>
          </div>
        `;
      }).join("");
    }

    function formatPercent(value) {
      return `${Math.round(value * 100)}%`;
    }

    function renderEvaluation(payload) {
      evalMetricsEl.innerHTML = `
        <div class="metric">
          <strong>${formatPercent(payload.pass_rate)}</strong>
          <span>Pass rate</span>
        </div>
        <div class="metric">
          <strong>${formatPercent(payload.average_citation_coverage)}</strong>
          <span>Citation coverage</span>
        </div>
        <div class="metric">
          <strong>${formatPercent(payload.average_expected_citation_recall)}</strong>
          <span>Expected citation recall</span>
        </div>
      `;
      evalResultsEl.innerHTML = payload.results.map((item) => `
        <div class="eval-row">
          <div>
            <strong>${escapeHtml(item.id)}</strong>
            <div class="meta">coverage ${formatPercent(item.citation_coverage)} · expected recall ${formatPercent(item.expected_citation_recall)}</div>
          </div>
          <span class="badge ${item.passed ? "pass" : "fail"}">${item.passed ? "PASS" : "FAIL"}</span>
        </div>
      `).join("");
    }

    async function refreshCases() {
      const cases = await requestJson("/cases");
      if (cases.length === 0) {
        selectedCaseId = null;
        caseListEl.innerHTML = '<p class="empty">No cases loaded.</p>';
        caseEvidenceEl.innerHTML = '<p class="empty">No case selected.</p>';
        return;
      }
      caseListEl.innerHTML = cases.map((item) => `
        <button type="button" class="case-row ${item.case_id === selectedCaseId ? "active" : ""}" data-case-id="${item.case_id}">
          <strong>${escapeHtml(item.title)}</strong>
          <div class="meta">${escapeHtml(item.claim_type)} · ${item.evidence_count} evidence items · ${escapeHtml(item.source)}</div>
        </button>
      `).join("");
      caseListEl.querySelectorAll("[data-case-id]").forEach((button) => {
        button.addEventListener("click", () => {
          selectedCaseId = button.dataset.caseId;
          refreshCases();
          setStatus(`Selected ${selectedCaseId}`);
        });
      });
      if (!selectedCaseId && cases[0]) selectedCaseId = cases[0].case_id;
      if (selectedCaseId) await loadSelectedCase();
    }

    async function loadSelectedCase() {
      if (!selectedCaseId) {
        caseEvidenceEl.innerHTML = '<p class="empty">No case selected.</p>';
        return;
      }
      const payload = await requestJson(`/cases/${selectedCaseId}`);
      renderCaseEvidence(payload);
    }

    async function importNhtsaCase() {
      setStatus("Importing NHTSA case...");
      const payload = {
        make: document.getElementById("make").value,
        model: document.getElementById("model").value,
        year: Number(document.getElementById("year").value),
        max_complaints: 10,
        max_recalls: 5
      };
      const created = await requestJson("/cases/import/nhtsa", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });
      selectedCaseId = created.case_id;
      await refreshCases();
      setStatus(`Imported ${created.title}`);
    }

    async function seedDemoCase() {
      setStatus("Seeding demo case...");
      const created = await requestJson("/cases/demo", {
        method: "POST"
      });
      selectedCaseId = created.case_id;
      await refreshCases();
      setStatus(`Seeded ${created.title}`);
    }

    async function createManualCase() {
      const evidenceContent = document.getElementById("manualEvidenceContent").value.trim();
      if (!evidenceContent) {
        setStatus("Manual case needs evidence text.", true);
        return;
      }
      setStatus("Creating manual case...");
      const payload = {
        title: document.getElementById("manualTitle").value.trim() || "Manual evidence review",
        claim_type: document.getElementById("manualClaimType").value.trim() || "auto_collision",
        source: "manual_dashboard",
        evidence: [
          {
            id: `manual-${Date.now()}`,
            type: "text",
            title: document.getElementById("manualEvidenceTitle").value.trim() || "Manual evidence note",
            content: evidenceContent,
            metadata: {source: "manual_dashboard"}
          }
        ]
      };
      const created = await requestJson("/cases", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });
      selectedCaseId = created.case_id;
      await refreshCases();
      setStatus(`Created ${created.title}`);
    }

    async function deleteSelectedCase() {
      if (!selectedCaseId) {
        setStatus("Select a case to delete.", true);
        return;
      }
      const deletingCaseId = selectedCaseId;
      setStatus(`Deleting ${deletingCaseId}...`);
      await requestJson(`/cases/${selectedCaseId}`, {
        method: "DELETE"
      });
      selectedCaseId = null;
      clearSelectedCasePanels();
      await refreshCases();
      setStatus(`Deleted ${deletingCaseId}`);
    }

    async function askSelectedCase() {
      if (!selectedCaseId) {
        setStatus("Import or select a case first.", true);
        return;
      }
      setStatus("Asking case...");
      const payload = await requestJson(`/cases/${selectedCaseId}/ask`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: document.getElementById("question").value})
      });
      renderAnswer(payload);
      setStatus("Answer ready");
    }

    async function generateReport() {
      if (!selectedCaseId) {
        setStatus("Import or select a case first.", true);
        return;
      }
      setStatus("Generating report...");
      const payload = await requestJson(`/cases/${selectedCaseId}/report`);
      renderReport(payload);
      setStatus("Report ready");
    }

    function exportMarkdownReport() {
      if (!selectedCaseId) {
        setStatus("Import or select a case first.", true);
        return;
      }
      window.open(`/cases/${selectedCaseId}/report.md`, "_blank");
      setStatus("Markdown report opened");
    }

    async function exportCaseBundle() {
      if (!selectedCaseId) {
        setStatus("Import or select a case first.", true);
        return;
      }
      setStatus("Exporting case bundle...");
      const payload = await requestJson(`/cases/${selectedCaseId}/bundle.json`);
      caseBundleJsonEl.value = JSON.stringify(payload, null, 2);
      setStatus("Case bundle ready");
    }

    async function importCaseBundle() {
      const rawBundle = caseBundleJsonEl.value.trim();
      if (!rawBundle) {
        setStatus("Paste a case bundle to import.", true);
        return;
      }
      let payload;
      try {
        payload = JSON.parse(rawBundle);
      } catch (error) {
        setStatus("Case bundle must be valid JSON.", true);
        return;
      }
      setStatus("Importing case bundle...");
      const created = await requestJson("/cases/import/bundle", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });
      selectedCaseId = created.case_id;
      await refreshCases();
      setStatus(`Imported ${created.title}`);
    }

    async function runEvaluations() {
      setStatus("Running evaluations...");
      const payload = await requestJson("/evals/demo");
      renderEvaluation(payload);
      setStatus(`Evaluations ready: ${payload.passed_count}/${payload.example_count} passed`);
    }

    document.getElementById("importButton").addEventListener("click", () => {
      importNhtsaCase().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("seedDemoButton").addEventListener("click", () => {
      seedDemoCase().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("refreshButton").addEventListener("click", () => {
      refreshCases().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("deleteCaseButton").addEventListener("click", () => {
      deleteSelectedCase().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("manualCreateButton").addEventListener("click", () => {
      createManualCase().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("askButton").addEventListener("click", () => {
      askSelectedCase().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("reportButton").addEventListener("click", () => {
      generateReport().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("exportMarkdownButton").addEventListener("click", () => {
      exportMarkdownReport();
    });
    document.getElementById("exportBundleButton").addEventListener("click", () => {
      exportCaseBundle().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("importBundleButton").addEventListener("click", () => {
      importCaseBundle().catch((error) => setStatus(error.message, true));
    });
    document.getElementById("evalButton").addEventListener("click", () => {
      runEvaluations().catch((error) => setStatus(error.message, true));
    });

    refreshCases().catch((error) => setStatus(error.message, true));
  </script>
</body>
</html>"""
