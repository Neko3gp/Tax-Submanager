import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { KIND_INFO } from "../utils";

// Pantalla "SeleccionPerfil" del diagrama de actividad.
export default function Workspaces() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/workspaces/").then(setItems).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!items) return <p className="muted">Cargando…</p>;

  return (
    <>
      <h1>Elige tu espacio de trabajo</h1>
      <p className="muted">Cada espacio aísla sus datos y aplica sus propias reglas de negocio.</p>
      <div className="grid three">
        {items.map((w) => {
          const info = KIND_INFO[w.kind];
          return (
            <Link key={w.id} to={`/w/${w.id}`} className="card ws-card">
              <div className="ws-icon">{info.icon}</div>
              <h2>{w.name}</h2>
              <span className={`badge ${w.kind}`}>{info.title}</span>
              <p className="muted">{info.text}</p>
            </Link>
          );
        })}
      </div>
    </>
  );
}
