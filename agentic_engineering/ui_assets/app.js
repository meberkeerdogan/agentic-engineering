"use strict";

const byId = (id) => document.getElementById(id);

let sessionToken = "";

function showNotice(message, isError = false) {
  const notice = byId("notice");
  notice.textContent = message;
  notice.classList.toggle("error", isError);
  notice.hidden = false;
}

function formatCost(summary) {
  if (summary.measured_cost === null || summary.measured_cost === undefined) return "—";
  return `${summary.measured_cost} ${summary.cost_unit || ""}`.trim();
}

function runCard(summary) {
  const card = document.createElement("article");
  card.className = "run-card";

  const identity = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = summary.run_id || "Unnamed run";
  const workflow = document.createElement("span");
  workflow.textContent = summary.task_id || summary.workflow_id || "Verified workflow";
  identity.append(title, workflow);

  const cost = document.createElement("span");
  cost.className = "run-cost";
  cost.textContent = formatCost(summary);

  const state = document.createElement("span");
  state.className = "run-state";
  state.textContent = summary.status || "unknown";
  card.append(identity, cost, state);
  return card;
}

function renderRecent(runs) {
  const list = byId("recent-runs");
  if (!Array.isArray(runs) || runs.length === 0) return;
  list.replaceChildren(...runs.map(runCard));
}

function renderResult(summary) {
  byId("result-panel").hidden = false;
  const status = byId("result-status");
  status.textContent = summary.status || "unknown";
  status.classList.toggle("verified", summary.verified_complete === true);
  byId("result-verified").textContent = summary.verified_complete ? "Yes" : "No";
  byId("result-regressions").textContent = Array.isArray(summary.regressions)
    ? String(summary.regressions.length)
    : "—";
  byId("result-cost").textContent = formatCost(summary);
  byId("result-time").textContent = summary.time_seconds === undefined
    ? "—"
    : `${summary.time_seconds}s`;
  byId("result-run-id").textContent = summary.run_id || "—";
  byId("result-revision").textContent = summary.workspace_revision || "—";
  byId("result-evaluation").textContent = summary.evaluation_ref || "—";
  byId("result-state").textContent = summary.state_ref || "—";
  renderRecent([summary]);
  byId("result-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function loadSession() {
  const response = await fetch("/api/session", { cache: "no-store" });
  if (!response.ok) throw new Error("Could not load the local session.");
  const session = await response.json();
  sessionToken = session.token;
  byId("workflow-id").textContent = session.workflow_id;
  byId("project-name").textContent = session.project_name;
  byId("project-root").textContent = session.project_root;
  byId("config").value = session.default_config;
  byId("run-id").value = `run-${new Date().toISOString().slice(0, 10)}`;
  renderRecent(session.recent_runs);
}

async function startRun(event) {
  event.preventDefault();
  const button = byId("run-button");
  button.disabled = true;
  button.textContent = "Running and verifying…";
  showNotice("The agent is working. Keep this page open; the result will appear here.");
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Agentic-Token": sessionToken,
      },
      body: JSON.stringify({
        config: byId("config").value.trim(),
        run_id: byId("run-id").value.trim(),
        confirm_paid_run: byId("confirm-paid-run").checked,
      }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "The run could not finish.");
    renderResult(result);
    showNotice(result.verified_complete
      ? "Run finished and the independent checks passed."
      : "Run finished, but the independent checks did not verify it.");
  } catch (error) {
    showNotice(error instanceof Error ? error.message : "The run failed.", true);
  } finally {
    button.disabled = false;
    button.textContent = "Run verified workflow";
  }
}

byId("run-form").addEventListener("submit", startRun);
loadSession().catch((error) => showNotice(error.message, true));
