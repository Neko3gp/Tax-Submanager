"""Catálogo de categorías y criterio de deducibilidad (Python puro, sin Django)."""

KINDS = ("personal", "universitario", "negocio")

CATEGORIES = {
    "personal": ["Streaming", "Música", "Almacenamiento", "Gimnasio", "Telefonía", "Otros"],
    "universitario": ["Software", "IDEs y herramientas", "Cursos", "Material académico", "Almacenamiento", "Otros"],
    "negocio": [
        "Software", "Internet", "Renta", "Publicidad", "Equipo",
        "Servicios profesionales", "Energía", "Entretenimiento", "Otros",
    ],
}

# Categorías que el motor trata como deducibles en el espacio "negocio".
# Es una regla informativa de la demo, NO asesoría fiscal.
DEDUCTIBLE_NEGOCIO = frozenset({
    "software", "internet", "renta", "publicidad", "equipo",
    "servicios profesionales", "energía",
})


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def is_deductible(category: str) -> bool:
    return normalize(category) in DEDUCTIBLE_NEGOCIO
