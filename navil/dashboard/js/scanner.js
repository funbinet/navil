export async function startScan(payload, token) {
  const response = await fetch("/api/scans", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Scan creation failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchFindings(scanId, token) {
  const path = scanId ? `/api/scans/${scanId}/findings` : "/api/findings";
  const response = await fetch(path, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Findings fetch failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchScan(scanId, token) {
  const response = await fetch(`/api/scans/${scanId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Scan fetch failed: ${response.status}`);
  }
  return response.json();
}
