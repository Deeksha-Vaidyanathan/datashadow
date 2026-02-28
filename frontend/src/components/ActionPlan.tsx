import type { RemediationItem } from "../api/client";

type Props = {
  items: RemediationItem[];
  onToggle: (item: RemediationItem) => void;
};

const priorityLabel = (p: number) => (p === 1 ? "High" : p === 2 ? "Medium" : "Low");

export default function ActionPlan({ items, onToggle }: Props) {
  if (items.length === 0) return null;
  return (
    <section className="action-plan">
      <h2>Prioritized action plan</h2>
      <ul className="action-list">
        {items
          .sort((a, b) => a.priority - b.priority)
          .map((item) => (
            <li
              key={item.id}
              className={`action-item ${item.completed ? "completed" : ""}`}
            >
              <label className="action-row">
                <input
                  type="checkbox"
                  checked={item.completed}
                  onChange={() => onToggle(item)}
                />
                <span className="action-title">{item.title}</span>
                <span className="action-priority">{priorityLabel(item.priority)}</span>
              </label>
              {item.link_or_instruction && (
                <p className="action-instruction">{item.link_or_instruction}</p>
              )}
            </li>
          ))}
      </ul>
    </section>
  );
}
