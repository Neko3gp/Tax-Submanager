import { useEffect, useState } from "react";
import { api } from "../api";

const fmt = (iso) => new Date(iso).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" });

// Módulo de backup manual: contingencia del riesgo R1 (pérdida de la base de datos local).
export default function Backups() {
  const [items, setItems] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => api("/backups/").then(setItems).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const create = async () => {
    setBusy(true); setError(""); setMessage("");
    try {
      const res = await api("/backups/", { method: "POST" });
      setMessage(`Respaldo creado: ${res.name}`);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const restore = async (name) => {
    const ok = window.confirm(
      "Se reemplazarán los pagos de TODOS tus espacios con los de este respaldo.\n" +
      "Antes se guardará un respaldo de seguridad automático. ¿Continuar?"
    );
    if (!ok) return;
    setBusy(true); setError(""); setMessage("");
    try {
      const res = await api(`/backups/${name}/restore/`, { method: "POST" });
      setMessage(`Restaurados ${res.restored_expenses} pagos. Respaldo de seguridad: ${res.safety_backup}`);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h1>Respaldos</h1>
      <p className="muted">
        Guarda una copia de tus espacios y pagos. Si algo se corrompe o se borra por error, puedes restaurarla.
      </p>
      <button className="btn" onClick={create} disabled={busy}>Crear respaldo ahora</button>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <section className="card" style={{ marginTop: 16 }}>
        {!items ? <p className="muted">Cargando…</p> : items.length === 0 ? (
          <p className="muted">Aún no hay respaldos.</p>
        ) : (
          <ul className="plain">
            {items.map((b) => (
              <li key={b.name} className="row">
                <span>{b.name}<br /><span className="muted small">{fmt(b.created_at)} · {(b.size / 1024).toFixed(1)} KB</span></span>
                <button className="btn ghost" disabled={busy} onClick={() => restore(b.name)}>Restaurar</button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
