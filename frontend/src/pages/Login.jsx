import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(form.username, form.password);
      navigate("/");
    } catch (err) {
      setError(err.status === 401 ? "Usuario o contraseña incorrectos." : err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="card auth-card" onSubmit={submit}>
        <h1>Tax SubManager</h1>
        <p className="muted">Asistente de suscripciones y deducciones</p>
        <label>Usuario
          <input value={form.username} autoFocus required
                 onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </label>
        <label>Contraseña
          <input type="password" value={form.password} required
                 onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Entrando…" : "Entrar"}</button>
        <p className="muted small">
          ¿No tienes cuenta? <Link to="/registro">Regístrate</Link> · Demo: <code>demo</code> / <code>demo12345</code>
        </p>
      </form>
    </div>
  );
}
