import { createRewardChart, createSeverityChart, pushRewardPoint, updateSeverityChart } from "./charts.js";
import { fetchFindings, fetchScan, startScan } from "./scanner.js";
import { ScanSocket } from "./websocket.js";

const state = {
  token: localStorage.getItem("navil_api_token") || "local-dev-token",
  scanId: null,
  socket: null,
};

const els = {
  token: document.querySelector("#api-token"),
  saveToken: document.querySelector("#save-token"),
  targetInput: document.querySelector("#target-input"),
  scopeInput: document.querySelector("#scope-input"),
  pluginsInput: document.querySelector("#plugins-input"),
  startScan: document.querySelector("#start-scan"),
  refreshFindings: document.querySelector("#refresh-findings"),
  scanMeta: document.querySelector("#scan-meta"),
  findingsTable: document.querySelector("#findings-table"),
  eventFeed: document.querySelector("#event-feed"),
  metricFindings: document.querySelector("#metric-findings"),
  metricCritical: document.querySelector("#metric-critical"),
  metricReward: document.querySelector("#metric-reward"),
  brainStatus: document.querySelector("#brain-status"),
};

const severityChart = createSeverityChart(document.querySelector("#severity-chart"));
const rewardChart = createRewardChart(document.querySelector("#reward-chart"));

els.token.value = state.token;

function renderFindings(findings) {
  els.findingsTable.innerHTML = "";
  for (const finding of findings) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="severity-${finding.severity.toLowerCase()}">${finding.severity}</td>
      <td>${finding.plugin}</td>
      <td>${finding.title}</td>
      <td title="${finding.url}">${finding.url}</td>
    `;
    els.findingsTable.appendChild(row);
  }

  const criticalOrHigh = findings.filter((item) => ["CRITICAL", "HIGH"].includes(item.severity)).length;
  els.metricFindings.textContent = String(findings.length);
  els.metricCritical.textContent = String(criticalOrHigh);
  updateSeverityChart(severityChart, findings);
}

function appendEvent(event) {
  const item = document.createElement("li");
  const now = new Date().toLocaleTimeString();
  item.textContent = `${now} | ${event.type}: ${event.message || "event"}`;
  els.eventFeed.prepend(item);
}

async function refreshFindings() {
  if (!state.scanId) {
    return;
  }
  const payload = await fetchFindings(state.scanId, state.token);
  renderFindings(payload.findings || []);
}

async function refreshScanStatus() {
  if (!state.scanId) {
    return;
  }
  const scan = await fetchScan(state.scanId, state.token);
  els.scanMeta.innerHTML = `
    <p><strong>Scan:</strong> ${scan.id}</p>
    <p><strong>Status:</strong> ${scan.status}</p>
    <p><strong>Endpoints:</strong> ${scan.metrics.discovered_endpoints}</p>
    <p><strong>Reward:</strong> ${scan.metrics.reward_score.toFixed(2)}</p>
  `;
  els.metricReward.textContent = scan.metrics.reward_score.toFixed(2);
  pushRewardPoint(rewardChart, scan.metrics.reward_score);
  els.brainStatus.textContent = `Updated ${new Date().toLocaleTimeString()} | status=${scan.status}`;
}

els.saveToken.addEventListener("click", () => {
  state.token = els.token.value.trim();
  localStorage.setItem("navil_api_token", state.token);
  appendEvent({ type: "auth", message: "API token saved" });
});

els.startScan.addEventListener("click", async () => {
  const targets = els.targetInput.value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  if (!targets.length) {
    appendEvent({ type: "error", message: "Add at least one target URL" });
    return;
  }

  const payload = {
    target_urls: targets,
    scope_path: els.scopeInput.value.trim() || ".navil-scope.yml",
    plugin_names: els.pluginsInput.value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
  };

  try {
    const result = await startScan(payload, state.token);
    state.scanId = result.scan_id;
    appendEvent({ type: "scan", message: `Started scan ${state.scanId}` });

    if (state.socket) {
      state.socket.close();
    }
    state.socket = new ScanSocket(state.scanId, (event) => {
      appendEvent(event);
      if (event.type === "complete" || event.type === "crawl" || event.type === "chains") {
        refreshScanStatus().catch(() => {});
        refreshFindings().catch(() => {});
      }
    });
    state.socket.connect();

    await refreshScanStatus();
  } catch (error) {
    appendEvent({ type: "error", message: error.message });
  }
});

els.refreshFindings.addEventListener("click", async () => {
  try {
    await refreshScanStatus();
    await refreshFindings();
    appendEvent({ type: "refresh", message: "Findings refreshed" });
  } catch (error) {
    appendEvent({ type: "error", message: error.message });
  }
});
