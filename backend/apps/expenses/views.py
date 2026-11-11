from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from apps.rules.engine import alerts_for_expense
from apps.workspaces.models import Workspace

from .models import Expense
from .serializers import ExpenseSerializer
from .services import workspace_alerts


class ExpenseViewSet(viewsets.ModelViewSet):
    """CRUD de gastos dentro de un espacio de trabajo del usuario autenticado."""

    serializer_class = ExpenseSerializer

    def get_workspace(self):
        # 404 si el espacio no existe o pertenece a otro usuario (aislamiento).
        return get_object_or_404(Workspace, pk=self.kwargs["workspace_id"], owner=self.request.user)

    def get_queryset(self):
        return Expense.objects.filter(workspace=self.get_workspace())

    def perform_create(self, serializer):
        serializer.save(workspace=self.get_workspace())

    def _with_alerts(self, response):
        """Adjunta las alertas del motor de reglas a la respuesta de create/update."""
        alerts = workspace_alerts(self.get_workspace())
        mine = alerts_for_expense(alerts, response.data.get("id"))
        response.data = {**response.data, "alerts": [a.to_dict() for a in mine]}
        return response

    def create(self, request, *args, **kwargs):
        return self._with_alerts(super().create(request, *args, **kwargs))

    def update(self, request, *args, **kwargs):
        return self._with_alerts(super().update(request, *args, **kwargs))
