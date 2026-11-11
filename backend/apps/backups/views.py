import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class BackupListCreateView(APIView):
    def get(self, request):
        return Response(services.list_backups(request.user))

    def post(self, request):
        path = services.create_backup(request.user)
        return Response({"name": path.name}, status=status.HTTP_201_CREATED)


class BackupRestoreView(APIView):
    def post(self, request, name):
        path = services.backup_path(request.user, name)
        if path is None:
            return Response({"detail": "Respaldo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return Response({"detail": "No se pudo leer el respaldo."}, status=status.HTTP_400_BAD_REQUEST)

        safety = services.create_backup(request.user)  # respaldo de seguridad antes de sobrescribir
        try:
            restored = services.restore_payload(request.user, payload)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"restored_expenses": restored, "safety_backup": safety.name})
