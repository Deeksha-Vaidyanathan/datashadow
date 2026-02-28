import type { ScanListItem } from "../api/client";

type Props = {
  scans: ScanListItem[];
  onSelect: (scanId: number) => void;
};

export default function ScanList({ scans, onSelect }: Props) {
  if (scans.length === 0) {
    return <p className="muted">No scans yet. Run a scan above.</p>;
  }
  return (
    <ul className="scan-list">
      {scans.map((s) => (
        <li key={s.id} className="scan-list-item">
          <button
            type="button"
            className="scan-list-btn"
            onClick={() => onSelect(s.id)}
          >
            <span className="scan-list-email">{s.email_or_username}</span>
            <span className="scan-list-score">Score: {s.exposure_score}</span>
            <span className="scan-list-meta">
              {new Date(s.created_at).toLocaleDateString()}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
