// Cliente de la API REST con JWT. Renueva el access token automáticamente una vez si recibe 401.
const BASE = "/api";

export const tokens = {
  get access() { return localStorage.getItem("access"); },
  get refresh() { return localStorage.getItem("refresh"); },
  set(access, refresh) {
    localStorage.setItem("access", access);
    if (refresh) localStorage.setItem("refresh", refresh);
  },
  clear() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  },
};

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function messageFrom(data) {
  if (!data) return "Error inesperado del servidor.";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  return Object.entries(data)
    .map(([campo, v]) => `${campo}: ${Array.isArray(v) ? v.join(" ") : v}`)
    .join(" · ");
}

let refreshing = null;

function refreshAccess() {
  if (!tokens.refresh) return Promise.resolve(false);
  if (!refreshing) {
    refreshing = fetch(`${BASE}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh }),
    })
      .then(async (res) => {
        if (!res.ok) return false;
        const data = await res.json();
        tokens.set(data.access, data.refresh);
        return true;
      })
      .catch(() => false)
      .finally(() => { refreshing = null; });
  }
  return refreshing;
}

/**
 * api("/workspaces/") · api("/x/", { method: "POST", body: {...} })
 * Pasa `auth: false` en login/registro (no hay sesión que renovar).
 */
export async function api(path, { method = "GET", body, auth = true, retried = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  let res;
  try {
    res = await fetch(BASE + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("No se pudo conectar con el servidor. ¿Está corriendo el backend?", 0, null);
  }

  if (res.status === 401 && auth && !retried && tokens.refresh) {
    if (await refreshAccess()) return api(path, { method, body, auth, retried: true });
    tokens.clear();
    window.location.assign("/login");
  }

  const data = res.status === 204 || res.status === 205 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(messageFrom(data), res.status, data);
  return data;
}
