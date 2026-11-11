"""Backup manual (plan de contingencia del riesgo R1: pérdida del archivo local).

Cada respaldo es un JSON con los espacios y gastos DEL USUARIO (no un volcado global,
para no exponer datos ni contraseñas de otros usuarios). Funciona igual con SQLite y PostgreSQL.
"""
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.db import transaction

from apps.expenses.serializers import ExpenseSerializer
from apps.workspaces.models import Workspace

FILENAME_RE = re.compile(r"^backup-\d{8}-\d{6}\.json$")
FORMAT_VERSION = 1


def user_dir(user) -> Path:
    path = Path(settings.BACKUP_DIR) / str(user.id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_payload(user) -> dict:
    workspaces = []
    for ws in Workspace.objects.filter(owner=user).prefetch_related("expenses"):
        workspaces.append({
            "kind": ws.kind,
            "name": ws.name,
            "monthly_budget": str(ws.monthly_budget) if ws.monthly_budget is not None else None,
            "expenses": [
                {
                    "name": e.name,
                    "amount": str(e.amount),
                    "cut_date": e.cut_date.isoformat(),
                    "category": e.category,
                    "frequency": e.frequency,
                }
                for e in ws.expenses.all()
            ],
        })
    return {
        "version": FORMAT_VERSION,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "username": user.username,
        "workspaces": workspaces,
    }


def create_backup(user) -> Path:
    name = datetime.now().strftime("backup-%Y%m%d-%H%M%S.json")
    path = user_dir(user) / name
    path.write_text(json.dumps(build_payload(user), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_backups(user):
    items = []
    for path in sorted(user_dir(user).glob("backup-*.json"), reverse=True):
        if not FILENAME_RE.match(path.name):
            continue
        stat = path.stat()
        items.append({
            "name": path.name,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        })
    return items


def backup_path(user, name):
    """Ruta segura de un respaldo del usuario, o None (el nombre debe cumplir el patrón)."""
    if not FILENAME_RE.match(name):
        return None
    path = user_dir(user) / name
    return path if path.is_file() else None


@transaction.atomic
def restore_payload(user, payload: dict) -> int:
    """Reemplaza los gastos del usuario con los del respaldo. Devuelve cuántos gastos restauró."""
    if not isinstance(payload, dict) or payload.get("version") != FORMAT_VERSION \
            or not isinstance(payload.get("workspaces"), list):
        raise ValueError("El archivo de respaldo no tiene un formato válido.")

    restored = 0
    for ws_data in payload["workspaces"]:
        ws = Workspace.objects.filter(owner=user, kind=ws_data.get("kind")).first()
        if ws is None:
            continue
        budget = ws_data.get("monthly_budget")
        ws.name = ws_data.get("name") or ws.name
        ws.monthly_budget = Decimal(budget) if budget is not None else None
        ws.save()
        ws.expenses.all().delete()
        for item in ws_data.get("expenses", []):
            serializer = ExpenseSerializer(data=item)
            serializer.is_valid(raise_exception=True)  # si algo falla, todo se revierte (atomic)
            serializer.save(workspace=ws)
            restored += 1
    return restored
