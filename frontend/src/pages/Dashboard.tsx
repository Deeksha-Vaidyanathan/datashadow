import { useState, useEffect } from "react";
import "./Dashboard.css";
import { useNavigate } from "react-router-dom";
import {
  createScan,
  listScans,
  getExposureHistory,
  type ScanListItem,
  type ExposureHistoryPoint,
} from "../api/client";
import ExposureChart from "../components/ExposureChart";
import ScanList from "../components/ScanList";

export default function Dashboard() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scans, setScans] = useState<ScanListItem[]>([]);
  const [history, setHistory] = useState<ExposureHistoryPoint[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadScans();
  }, []);

  async function loadScans(email?: string) {
    try {
      const data = await listScans(email);
      setScans(data);
      if (email) {
        const h = await getExposureHistory(email);
        setHistory(h);
        setSelectedEmail(email);
      } else {
        setHistory([]);
        setSelectedEmail(null);
      }
    } catch {
      setScans([]);
      setHistory([]);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const value = input.trim();
    if (!value) return;
    setError(null);
    setLoading(true);
    try {
      const scan = await createScan(value);
      await loadScans(value);
      navigate(`/scan/${scan.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dashboard">
      <header className="header">
        <h1 className="logo">
          <span className="logo-icon">◇</span> DataShadow
        </h1>
        <p className="tagline">Personal Data Exposure Auditor</p>
      </header>

      <section className="hero">
        <p className="hero-text">
          Enter your email or username to see how much of your personal data is exposed online —
          breaches, pastes, and data brokers. Get a prioritized action plan to lock things down.
        </p>
        <form onSubmit={handleSubmit} className="scan-form">
          <input
            type="text"
            placeholder="Email or username"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="scan-input"
            disabled={loading}
          />
          <button type="submit" className="scan-btn" disabled={loading}>
            {loading ? "Scanning…" : "Run scan"}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      {history.length > 0 && (
        <section className="chart-section">
          <h2>Exposure score over time</h2>
          <p className="muted">{selectedEmail}</p>
          <ExposureChart data={history} />
        </section>
      )}

      <section className="scans-section">
        <h2>Recent scans</h2>
        <ScanList scans={scans} onSelect={(id) => navigate(`/scan/${id}`)} />
      </section>
    </div>
  );
}
