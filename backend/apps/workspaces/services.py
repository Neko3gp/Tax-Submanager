from decimal import Decimal

from .models import Workspace

# (tipo, nombre, presupuesto mensual inicial)
DEFAULT_WORKSPACES = [
    ("personal", "Personal", None),
    ("universitario", "Universitario", Decimal("1500.00")),
    ("negocio", "Mi negocio", None),
]


def create_default_workspaces(user):
    """Crea los tres espacios aislados de un usuario (idempotente)."""
    for kind, name, budget in DEFAULT_WORKSPACES:
        Workspace.objects.get_or_create(
            owner=user, kind=kind, defaults={"name": name, "monthly_budget": budget}
        )
