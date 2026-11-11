import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, tokens } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  // Al abrir la app, si hay token se intenta recuperar la sesión.
  useEffect(() => {
    if (!tokens.access) { setReady(true); return; }
    api("/auth/me/")
      .then(setUser)
      .catch(() => tokens.clear())
      .finally(() => setReady(true));
  }, []);

  const login = useCallback(async (username, password) => {
    const data = await api("/auth/login/", { method: "POST", body: { username, password }, auth: false });
    tokens.set(data.access, data.refresh);
    setUser(await api("/auth/me/"));
  }, []);

  const register = useCallback(async (username, email, password) => {
    const data = await api("/auth/register/", { method: "POST", body: { username, email, password }, auth: false });
    tokens.set(data.access, data.refresh);
    setUser(data.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api("/auth/logout/", { method: "POST", body: { refresh: tokens.refresh } });
    } catch { /* si falla igual cerramos la sesión local */ }
    tokens.clear();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
