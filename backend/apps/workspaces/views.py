from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.rules.catalog import CATEGORIES

from .models import Workspace
from .serializers import WorkspaceSerializer


class WorkspaceListView(generics.ListAPIView):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(owner=self.request.user)


class WorkspaceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        # Solo los espacios del usuario autenticado: el aislamiento vive aquí.
        return Workspace.objects.filter(owner=self.request.user)


@api_view(["GET"])
def categories(request):
    return Response({"categories": CATEGORIES})
