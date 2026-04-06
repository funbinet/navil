const severityPalette = {
  CRITICAL: "#ff3b4a",
  HIGH: "#ff6a55",
  MEDIUM: "#ffb84d",
  LOW: "#4dffa8",
  INFO: "#4ad7ff",
};

export function createSeverityChart(canvas) {
  return new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
      datasets: [{
        data: [0, 0, 0, 0, 0],
        backgroundColor: [
          severityPalette.CRITICAL,
          severityPalette.HIGH,
          severityPalette.MEDIUM,
          severityPalette.LOW,
          severityPalette.INFO,
        ],
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: "#c7d9e7" } },
      },
    },
  });
}

export function createRewardChart(canvas) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Reward",
        data: [],
        borderColor: "#00d8a7",
        backgroundColor: "rgba(0,216,167,0.2)",
        tension: 0.25,
      }],
    },
    options: {
      responsive: true,
      scales: {
        x: { ticks: { color: "#9ab7ca" } },
        y: { ticks: { color: "#9ab7ca" } },
      },
      plugins: {
        legend: { labels: { color: "#c7d9e7" } },
      },
    },
  });
}

export function updateSeverityChart(chart, findings) {
  const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0 };
  for (const finding of findings) {
    const severity = finding.severity;
    if (counts[severity] !== undefined) {
      counts[severity] += 1;
    }
  }
  chart.data.datasets[0].data = [
    counts.CRITICAL,
    counts.HIGH,
    counts.MEDIUM,
    counts.LOW,
    counts.INFO,
  ];
  chart.update();
}

export function pushRewardPoint(chart, reward) {
  const nextIndex = chart.data.labels.length + 1;
  chart.data.labels.push(String(nextIndex));
  chart.data.datasets[0].data.push(reward);
  chart.update();
}
