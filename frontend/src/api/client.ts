const API_BASE = "/api";

export type ScanResult = {
  id: number;
  email_or_username: string;
  exposure_score: number;
  breach_count: number;
  paste_count: number;
  data_broker_flags: number;
  raw_results?: {
    breaches?: unknown[];
    pastes?: unknown[];
    data_brokers?: { name: string; opt_out_url: string; description: string }[];
  };
  action_plan?: { summary: string; actions: ActionPlanItem[] };
  created_at: string;
};

export type ActionPlanItem = {
  title: string;
  category: string;
  priority: number;
  link_or_instruction?: string;
};

export type ScanListItem = {
  id: number;
  email_or_username: string;
  exposure_score: number;
  breach_count: number;
  paste_count: number;
  data_broker_flags: number;
  created_at: string;
};

export type ExposureHistoryPoint = {
  date: string;
  exposure_score: number;
  scan_id: number;
};

export type RemediationItem = {
  id: number;
  scan_id: number;
  title: string;
  category: string;
  priority: number;
  link_or_instruction: string | null;
  completed: boolean;
  completed_at: string | null;
  created_at: string;
};

export async function createScan(emailOrUsername: string): Promise<ScanResult> {
  const r = await fetch(`${API_BASE}/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email_or_username: emailOrUsername }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || "Scan failed");
  }
  return r.json();
}

export async function listScans(emailOrUsername?: string): Promise<ScanListItem[]> {
  const url = emailOrUsername
    ? `${API_BASE}/scans?email_or_username=${encodeURIComponent(emailOrUsername)}`
    : `${API_BASE}/scans`;
  const r = await fetch(url);
  if (!r.ok) throw new Error("Failed to list scans");
  return r.json();
}

export async function getScan(scanId: number): Promise<ScanResult> {
  const r = await fetch(`${API_BASE}/scans/${scanId}`);
  if (!r.ok) throw new Error("Scan not found");
  return r.json();
}

export async function getExposureHistory(emailOrUsername: string): Promise<ExposureHistoryPoint[]> {
  const r = await fetch(
    `${API_BASE}/scans/history?email_or_username=${encodeURIComponent(emailOrUsername)}`
  );
  if (!r.ok) throw new Error("Failed to load history");
  return r.json();
}

export async function listRemediation(scanId: number): Promise<RemediationItem[]> {
  const r = await fetch(`${API_BASE}/scans/${scanId}/remediation`);
  if (!r.ok) throw new Error("Failed to load remediation");
  return r.json();
}

export async function updateRemediation(
  scanId: number,
  itemId: number,
  completed: boolean
): Promise<RemediationItem> {
  const r = await fetch(`${API_BASE}/scans/${scanId}/remediation/${itemId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed }),
  });
  if (!r.ok) throw new Error("Update failed");
  return r.json();
}
