import { useEffect, useState } from "react";
import { NavLink, Outlet, useParams } from "react-router-dom";
import { api } from "../api";
import { KIND_INFO } from "../utils";

export default function WorkspaceLayout() {
  const { id } = useParams();
  const [workspace, setWorkspace] = useState(null);
  const [error, setError] = useState("");

  const load = () =>
    api(`/workspaces/${id}/`).then(setWorkspace).catch((e) => setError(e.message));

  useEffect(() => { setWorkspace(null); setError(""); load(); }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!workspace) return <p className="muted">Cargando espacio…</p>;

  const info = KIND_INFO[workspace.kind];
  return (
    <>
      <div className="ws-head">
        <h1>{info.icon} {workspace.name}</h1>
        <span className={`badge ${workspace.kind}`}>{info.title}</span>
      </div>
      <nav className="tabs">
        <NavLink to={`/w/${id}`} end>Dashboard</NavLink>
        <NavLink to={`/w/${id}/gastos`}>Gastos</NavLink>
      </nav>
      <Outlet context={{ workspace, reloadWorkspace: load }} />
    </>
  );
}
