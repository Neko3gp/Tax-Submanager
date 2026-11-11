import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const salir = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <>
      <header className="topbar">
        <Link to="/" className="brand">Tax SubManager</Link>
        <nav>
          <NavLink to="/" end>Espacios</NavLink>
          <NavLink to="/respaldos">Respaldos</NavLink>
        </nav>
        <div className="spacer" />
        <span className="muted">{user?.username}</span>
        <button className="btn ghost" onClick={salir}>Cerrar sesión</button>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}
