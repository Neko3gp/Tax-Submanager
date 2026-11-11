"""Crea un usuario demo con datos de ejemplo en los tres espacios.

Uso: python manage.py seed_demo
Usuario: demo · Contraseña: demo12345
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.expenses.models import Expense
from apps.workspaces.models import Workspace
from apps.workspaces.services import create_default_workspaces

DEMO_USER = "demo"
DEMO_PASSWORD = "demo12345"

# (tipo, nombre, monto, días desde hoy para el corte, categoría, periodicidad)
SAMPLE = [
    ("personal", "Netflix", "219.00", 3, "Streaming", "mensual"),
    ("personal", "Spotify", "129.00", 9, "Música", "mensual"),
    ("personal", "iCloud 200 GB", "49.00", 14, "Almacenamiento", "mensual"),
    ("universitario", "Licencia de IDE", "350.00", 5, "IDEs y herramientas", "mensual"),
    ("universitario", "Curso en línea", "899.00", 12, "Cursos", "mensual"),
    ("universitario", "Overleaf", "180.00", 20, "Software", "mensual"),
    ("universitario", "Notion Plus", "200.00", 25, "Software", "mensual"),
    ("negocio", "Hosting VPS", "150.00", 4, "Software", "mensual"),
    ("negocio", "Internet de la oficina", "599.00", 8, "Internet", "mensual"),
    ("negocio", "Renta del local", "4500.00", 2, "Renta", "mensual"),
    ("negocio", "Cena con el equipo", "850.00", 16, "Entretenimiento", "mensual"),
    ("negocio", "Dominio web", "300.00", 40, "Software", "anual"),
]


class Command(BaseCommand):
    help = "Crea (si no existe) el usuario demo con gastos de ejemplo."

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=DEMO_USER)
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        create_default_workspaces(user)

        workspaces = {w.kind: w for w in Workspace.objects.filter(owner=user)}
        if Expense.objects.filter(workspace__in=workspaces.values()).exists():
            self.stdout.write("El usuario demo ya tiene datos; no se agregó nada.")
            return

        today = timezone.localdate()
        for kind, name, amount, days, category, frequency in SAMPLE:
            Expense.objects.create(
                workspace=workspaces[kind],
                name=name,
                amount=Decimal(amount),
                cut_date=today + timedelta(days=days),
                category=category,
                frequency=frequency,
            )
        self.stdout.write(self.style.SUCCESS(
            f"Usuario demo listo ({DEMO_USER} / {DEMO_PASSWORD}) con {len(SAMPLE)} gastos de ejemplo."
        ))
