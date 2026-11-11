export const money = (value) =>
  Number(value).toLocaleString("es-MX", { style: "currency", currency: "MXN" });

export const todayISO = () => new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD en hora local

export const formatDate = (iso) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" });

const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
export const monthLabel = (yyyymm) => {
  const [y, m] = yyyymm.split("-");
  return `${MESES[Number(m) - 1]} ${y.slice(2)}`;
};

export const KIND_INFO = {
  personal: { icon: "👤", title: "Personal", text: "Suscripciones y pagos regulares del día a día." },
  universitario: { icon: "🎓", title: "Universitario", text: "Software, IDEs y cursos, con alerta de presupuesto académico." },
  negocio: { icon: "💼", title: "Negocio pequeño", text: "Gastos operativos con recomendaciones de deducibilidad." },
};
