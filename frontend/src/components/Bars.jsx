import { money } from "../utils";

/** Gráfica de barras horizontal hecha solo con CSS. items: [{ label, value }] */
export default function Bars({ items, empty = "Sin datos todavía." }) {
  if (!items || items.length === 0) return <p className="muted">{empty}</p>;
  const max = Math.max(...items.map((i) => Number(i.value)), 1);
  return (
    <div className="bars">
      {items.map((i) => (
        <div className="bar-row" key={i.label}>
          <span className="bar-label">{i.label}</span>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${(Number(i.value) / max) * 100}%` }} />
          </div>
          <span className="bar-value">{money(i.value)}</span>
        </div>
      ))}
    </div>
  );
}
