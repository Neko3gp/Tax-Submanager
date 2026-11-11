import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Layout from "./components/Layout.jsx";
import WorkspaceLayout from "./components/WorkspaceLayout.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Workspaces from "./pages/Workspaces.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Expenses from "./pages/Expenses.jsx";
import Backups from "./pages/Backups.jsx";

function Protected({ children }) {
  const { user, ready } = useAuth();
  if (!ready) return <p className="center muted">Cargando…</p>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Register />} />
      <Route element={<Protected><Layout /></Protected>}>
        <Route path="/" element={<Workspaces />} />
        <Route path="/respaldos" element={<Backups />} />
        <Route path="/w/:id" element={<WorkspaceLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="gastos" element={<Expenses />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
