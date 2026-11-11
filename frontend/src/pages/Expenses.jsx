import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from "../api";
import { formatDate, money, todayISO } from "../utils";
import AlertList from "../components/AlertList.jsx";

const emptyForm = () => ({ name: "", amount: "", cut_date: todayISO(), category: "", frequency: "mensual" });

export default function Expenses() {
  const { workspace, reloadWorkspace } = useOutletContext();
  const base = `/workspaces/${workspace.id}`;

  const [items, setItems] = useState(null);
  const [suggested, setSuggested] = useState([]);
  const [form, setForm] = useState(emptyForm());
  const [editingId, setEditingId] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");
  const [budget, setBudget] = useState(workspace.monthly_budget ?? "");

  const load = () => api(`${base}/expenses/`).then(setItems).catch((e) => setError(e.message));

  useEffect(() => {
    setItems(null); setAlerts([]); setEditingId(null); setForm(emptyForm());
    setBudget(workspace.monthly_budget ?? "");
    load();
    api("/categories/").then((d) => setSuggested(d.categories[workspace.kind] || []));
  }, [workspace.id]);

  const save = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const url = editingId ? `${base}/expenses/${editingId}/` : `${base}/expenses/`;
      const res = await api(url, { method: editingId ? "PUT" : "POST", body: form });
      setAlerts(res.alerts || []);
      setForm(emptyForm());
      setEditingId(null);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const edit = (x) => {
    setEditingId(x.id);
    setForm({ name: x.name, amount: x.amount, cut_date: x.cut_date, category: x.category, frequency: x.frequency });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const remove = async (x) => {
    if (!window.confirm(`¿Eliminar «${x.name}»?`)) return;
    await api(`${base}/expenses/${x.id}/`, { method: "DELETE" });
    setAlerts([]);
    load();
  };

  const saveBudget = async () => {
    setError("");
    try {
      await api(`/workspaces/${workspace.id}/`, {
        method: "PATCH",
        body: { monthly_budget: budget === "" ? null : budget },
      });
      reloadWorkspace();
      setAlerts([]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      {workspace.kind === "universitario" && (
        <div className="card inline-form">
          <label>Presupuesto mensual académico (MXN)
            <input type="number" min="0" step="0.01" value={budget} onChange={(e) => setBudget(e.target.value)} />
          </label>
          <button className="btn ghost" type="button" onClick={saveBudget}>Guardar presupuesto</button>
        </div>
      )}

      <form className="card form-grid" onSubmit={save}>
        <h2>{editingId ? "Editar pago" : "Nuevo pago periódico"}</h2>
        <label>Nombre
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label>Monto (MXN)
          <input required type="number" min="0.01" step="0.01" value={form.amount}
                 onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        </label>
        <label>Fecha de corte
          <input required type="date" value={form.cut_date}
                 onChange={(e) => setForm({ ...form, cut_date: e.target.value })} />
        </label>
        <label>Categoría
          <input required list="categorias" value={form.category}
                 onChange={(e) => setForm({ ...form, category: e.target.value })} />
          <datalist id="categorias">{suggested.map((c) => <option key={c} value={c} />)}</datalist>
        </label>
        <label>Periodicidad
          <select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
            <option value="mensual">Mensual</option>
            <option value="anual">Anual</option>
          </select>
        </label>
        <div className="actions">
          <button className="btn">{editingId ? "Guardar cambios" : "Agregar pago"}</button>
          {editingId && (
            <button type="button" className="btn ghost" onClick={() => { setEditingId(null); setForm(emptyForm()); }}>
              Cancelar
            </button>
          )}
        </div>
        {error && <p className="error">{error}</p>}
      </form>

      <AlertList alerts={alerts} />

      <section className="card">
        <h2>Pagos registrados</h2>
        {!items ? <p className="muted">Cargando…</p> : items.length === 0 ? (
          <p className="muted">Aún no hay pagos en este espacio.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Nombre</th><th>Categoría</th><th>Periodicidad</th><th>Corte</th><th className="num">Monto</th><th /></tr>
              </thead>
              <tbody>
                {items.map((x) => (
                  <tr key={x.id}>
                    <td>{x.name}</td>
                    <td>{x.category}</td>
                    <td>{x.frequency}</td>
                    <td>{formatDate(x.cut_date)}</td>
                    <td className="num">{money(x.amount)}</td>
                    <td className="num">
                      <button className="link" onClick={() => edit(x)}>Editar</button>
                      <button className="link danger" onClick={() => remove(x)}>Eliminar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
