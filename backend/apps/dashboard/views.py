from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.expenses.services import workspace_data
from apps.rules.engine import CENT, ZERO, deductible_monthly, evaluate, monthly_total
from apps.workspaces.models import Workspace

from . import calculations


def money(value):
    return str(value.quantize(CENT))


class DashboardView(APIView):
    """Proyecciones y alertas calculadas solo con los datos del espacio activo."""

    def get(self, request, workspace_id):
        ws = get_object_or_404(Workspace, pk=workspace_id, owner=request.user)
        expenses = workspace_data(ws)
        today = timezone.localdate()
        total = monthly_total(expenses)

        budget = None
        if ws.kind == Workspace.Kind.UNIVERSITARIO and ws.monthly_budget:
            budget = {
                "limit": money(ws.monthly_budget),
                "used": money(total),
                "percent": round(float(total / ws.monthly_budget * 100), 1),
            }

        alerts = evaluate(ws.kind, expenses, ws.monthly_budget)
        deductible = money(deductible_monthly(expenses)) if ws.kind == Workspace.Kind.NEGOCIO else None

        return Response({
            "workspace": {"id": ws.id, "name": ws.name, "kind": ws.kind},
            "today": today.isoformat(),
            "monthly_total": money(total),
            "expense_count": len(expenses),
            "by_category": [
                {"category": c, "total": money(t)} for c, t in calculations.by_category(expenses)
            ],
            "upcoming": [
                {"id": e.id, "name": e.name, "amount": money(e.amount), "date": d.isoformat(), "days_left": left}
                for e, d, left in calculations.upcoming(expenses, today)
            ],
            "projection": [
                {"month": m, "total": money(t)} for m, t in calculations.projection(expenses, today)
            ],
            "alerts": [a.to_dict() for a in alerts],
            "budget": budget,
            "deductible_monthly": deductible,
        })
