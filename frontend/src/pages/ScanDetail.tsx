import { useEffect, useState } from "react";
import "./ScanDetail.css";
import { useParams, useNavigate } from "react-router-dom";
import { getScan, listRemediation, updateRemediation, type ScanResult, type RemediationItem } from "../api/client";
import ActionPlan from "../components/ActionPlan";
import ExposureGauge from "../components/ExposureGauge";

export default function ScanDetail() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [remediation, setRemediation] = useState<RemediationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const id = scanId ? parseInt(scanId, 10) : NaN;

  useEffect(() => {
    if (!id || isNaN(id)) {
      setLoading(false);
      setError("Invalid scan");
      return;
    }
    (async () => {
      try {
        const [s, r] = await Promise.all([getScan(id), listRemediation(id)]);
        setScan(s);
        setRemediation(r);
      } catch {
        setError("Failed to load scan");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  async function toggleRemediation(item: RemediationItem) {
    try {
      const updated = await updateRemediation(id, item.id, !item.completed);
      setRemediation((prev) =>
        prev.map((i) => (i.id === updated.id ? updated : i))
      );
    } catch {
      // ignore
    }
  }

  if (loading) return <div className="page-loading">Loading scan…</div>;
  if (error || !scan) return <div className="page-error">{error || "Not found"}</div>;

  const brokers = scan.raw_results?.data_brokers ?? [];
  const breaches = scan.raw_results?.breaches ?? [];

  return (
    <div className="scan-detail">
      <header className="detail-header">
        <button type="button" className="back-btn" onClick={() => navigate("/")}>
          ← Dashboard
        </button>
        <h1>Scan: {scan.email_or_username}</h1>
        <p className="muted">{new Date(scan.created_at).toLocaleString()}</p>
      </header>

      <div className="score-block">
        <ExposureGauge score={scan.exposure_score} />
        <div className="stats">
          <div className="stat">
            <span className="stat-value">{scan.breach_count}</span>
            <span className="stat-label">Breaches</span>
          </div>
          <div className="stat">
            <span className="stat-value">{scan.paste_count}</span>
            <span className="stat-label">Pastes</span>
          </div>
          <div className="stat">
            <span className="stat-value">{scan.data_broker_flags}</span>
            <span className="stat-label">Data brokers</span>
          </div>
        </div>
      </div>

      {scan.action_plan?.summary && (
        <section className="summary-block">
          <h2>Summary</h2>
          <p>{scan.action_plan.summary}</p>
        </section>
      )}

      <ActionPlan
        items={remediation}
        onToggle={toggleRemediation}
      />

      <section className="raw-section">
        <h2>Breaches</h2>
        {breaches.length === 0 ? (
          <p className="muted">None found for this account.</p>
        ) : (
          <ul className="breach-list">
            {(breaches as { Name?: string; BreachDate?: string; DataClasses?: string[] }[]).map((b, i) => (
              <li key={i}>
                <strong>{b.Name ?? "Unknown"}</strong>
                {b.BreachDate && ` — ${b.BreachDate}`}
                {b.DataClasses?.length ? ` (${b.DataClasses.join(", ")})` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="raw-section">
        <h2>Data brokers (opt-out)</h2>
        {brokers.length === 0 ? (
          <p className="muted">No broker list for this scan.</p>
        ) : (
          <ul className="broker-list">
            {brokers.map((b) => (
              <li key={b.name}>
                <a href={b.opt_out_url} target="_blank" rel="noopener noreferrer">
                  {b.name}
                </a>
                {b.description && <span className="muted"> — {b.description}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
