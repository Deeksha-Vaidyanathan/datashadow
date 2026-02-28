import { useEffect, useState } from "react";
import "./ScanDetail.css";
import { useParams, useNavigate } from "react-router-dom";
import { getScan, listRemediation, updateRemediation, type ScanResult, type RemediationItem, type Breach, type Paste } from "../api/client";
import ActionPlan from "../components/ActionPlan";
import ExposureGauge from "../components/ExposureGauge";

/** Strip HTML tags for safe plain-text display of HIBP descriptions */
function stripHtml(html: string): string {
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.textContent ?? div.innerText ?? html;
}

/** Short "what was compromised" and "what to do" from data classes */
function breachRisks(dataClasses: string[] = []): { compromised: string; action: string } {
  const lower = dataClasses.map((c) => c.toLowerCase());
  const hasPasswords = lower.some((c) => c.includes("password"));
  const hasEmails = lower.some((c) => c.includes("email") || c.includes("e-mail"));
  const hasPersonal = lower.some((c) => c.includes("name") || c.includes("address") || c.includes("phone") || c.includes("birth"));
  let action = "Review the breach details and secure any related accounts.";
  if (hasPasswords) action = "Change the password for this service and any site where you reused it. Use a unique, strong password.";
  else if (hasEmails || hasPersonal) action = "Consider changing the account password and enabling 2FA. Watch for phishing targeting this email.";
  return {
    compromised: dataClasses.length ? dataClasses.join(", ") : "Various account data",
    action,
  };
}

/** Paste service URL when known (e.g. Pastebin) */
function pasteUrl(source: string, id: string): string | null {
  if (source === "Pastebin") return `https://pastebin.com/${id}`;
  if (source === "Ghostbin") return `https://ghostbin.com/paste/${id}`;
  return null;
}

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
  const breaches: Breach[] = scan.raw_results?.breaches ?? [];
  const pastes: Paste[] = scan.raw_results?.pastes ?? [];

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

      <section className="raw-section exposure-section">
        <h2>Data breaches</h2>
        <p className="section-intro">
          Your account was found in the following data breaches. Each entry is a service or site that was hacked and had its user data leaked; your email or username was in that leaked set.
        </p>
        {breaches.length === 0 ? (
          <p className="muted">None found for this account.</p>
        ) : (
          <div className="breach-cards">
            {breaches.map((b, i) => {
              const { compromised, action } = breachRisks(b.DataClasses);
              const title = b.Title ?? b.Name ?? "Unknown breach";
              const description = b.Description ? stripHtml(b.Description) : null;
              return (
                <div key={`${b.Name}-${i}`} className="breach-card">
                  <div className="breach-card-header">
                    <span className="breach-title">{title}</span>
                    {b.BreachDate && <span className="breach-date">Breach date: {b.BreachDate}</span>}
                  </div>
                  {b.PwnCount != null && (
                    <p className="breach-meta">
                      ~{b.PwnCount.toLocaleString()} accounts affected in this breach
                    </p>
                  )}
                  <p className="breach-what">
                    <strong>What was exposed:</strong> {compromised}
                  </p>
                  {description && (
                    <p className="breach-description">{description}</p>
                  )}
                  <p className="breach-action">
                    <strong>What you should do:</strong> {action}
                  </p>
                  {b.DataClasses && b.DataClasses.length > 0 && (
                    <div className="data-classes">
                      {b.DataClasses.map((dc) => (
                        <span key={dc} className="data-class-tag">{dc}</span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>

      <section className="raw-section exposure-section">
        <h2>Pastes</h2>
        <p className="section-intro">
          Your email appeared in one or more &quot;pastes&quot; — text dumps posted on sites like Pastebin. These often contain leaked credentials, account lists, or scraped data. Finding your email here means it may be in the hands of attackers or used for phishing.
        </p>
        {pastes.length === 0 ? (
          <p className="muted">None found for this account.</p>
        ) : (
          <div className="paste-cards">
            {pastes.map((p, i) => {
              const url = pasteUrl(p.Source, p.Id);
              const dateStr = p.Date ? new Date(p.Date).toLocaleDateString(undefined, { dateStyle: "medium" }) : null;
              return (
                <div key={`${p.Source}-${p.Id}-${i}`} className="paste-card">
                  <div className="paste-card-header">
                    <span className="paste-source">{p.Source}</span>
                    {dateStr && <span className="paste-date">{dateStr}</span>}
                  </div>
                  {p.Title && <p className="paste-title">{p.Title}</p>}
                  {p.EmailCount != null && (
                    <p className="paste-meta">
                      {p.EmailCount.toLocaleString()} email(s) found in this paste
                    </p>
                  )}
                  <p className="paste-what">
                    Your address was included in this paste. Such dumps are often from credential leaks or scrapers. Enable two-factor authentication on important accounts and be cautious of phishing targeting this email.
                  </p>
                  {url && (
                    <a href={url} target="_blank" rel="noopener noreferrer" className="paste-link">
                      View paste on {p.Source} (external)
                    </a>
                  )}
                </div>
              );
            })}
          </div>
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
