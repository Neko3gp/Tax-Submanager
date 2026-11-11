export default function AlertList({ alerts }) {
  if (!alerts || alerts.length === 0) return null;
  return (
    <ul className="alerts">
      {alerts.map((a, i) => (
        <li key={`${a.code}-${a.expense_id ?? "ws"}-${i}`} className={`alert ${a.level}`}>
          <span className="alert-icon">{a.level === "warning" ? "⚠️" : "🧾"}</span>
          {a.message}
        </li>
      ))}
    </ul>
  );
}
