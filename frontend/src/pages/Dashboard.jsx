import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import { api } from "../api";
import { formatDate, money, monthLabel } from "../utils";
import AlertList from "../components/AlertList.jsx";
import Bars from "../components/Bars.jsx";

export default function Dashboard() {
  const { workspace } = useOutletContext();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null);
    api(`/workspaces/${workspace.id}/dashboard/`).then(setData).catch((e) => setError(e.message));
  }, [workspace.id]);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="muted">Calculando…</p>;

  if (data.expense_count === 0) {
    return (
      <div className="card">
        <p>Este espacio todavía no tiene pagos registrados.</p>
        <Link className="btn" to={`/w/${workspace.id}/gastos`}>Registrar el primero</Link>
      </div>
    );
  }

  const yearTotal = data.projection.reduce((s, m) => s + Number(m.total), 0);

  return (
    <>
      <AlertList alerts={data.alerts} />

      <div className="grid four">
        <div className="card stat"><span className="muted">Total mensual</span><strong>{money(data.monthly_total)}</strong></div>
        <div className="card stat"><span className="muted">Pagos registrados</span><strong>{data.expense_count}</strong></div>
        <div className="card stat"><span className="muted">Próximos 12 meses</span><strong>{money(yearTotal)}</strong></div>
        {data.deductible_monthly !== null && (
          <div className="card stat"><span className="muted">Deducible al mes</span><strong>{money(data.deductible_monthly)}</strong></div>
        )}
        {data.budget && (
          <div className="card stat">
            <span className="muted">Presupuesto usado</span>
            <strong className={data.budget.percent > 100 ? "over" : ""}>{data.budget.percent}%</strong>
            <div className="meter"><div className={data.budget.percent > 100 ? "over" : ""}
                 style={{ width: `${Math.min(data.budget.percent, 100)}%` }} /></div>
            <span className="muted small">{money(data.budget.used)} de {money(data.budget.limit)}</span>
          </div>
        )}
      </div>

      <div className="grid two">
        <section className="card">
          <h2>Gasto mensual por categoría</h2>
          <Bars items={data.by_category.map((c) => ({ label: c.category, value: c.total }))} />
        </section>
        <section className="card">
          <h2>Próximos cortes (30 días)</h2>
          {data.upcoming.length === 0 ? <p className="muted">No hay cortes en los próximos 30 días.</p> : (
            <ul className="plain">
              {data.upcoming.map((u) => (
                <li key={u.id} className="row">
                  <span>{u.name}<br /><span className="muted small">{formatDate(u.date)} · {u.days_left === 0 ? "hoy" : `en ${u.days_left} d`}</span></span>
                  <strong>{money(u.amount)}</strong>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <section className="card">
        <h2>Proyección de pagos a 12 meses</h2>
        <Bars items={data.projection.map((m) => ({ label: monthLabel(m.month), value: m.total }))} />
      </section>
    </>
  );
}
