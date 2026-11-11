from django.urls import path

from .views import DashboardView

urlpatterns = [
    path("workspaces/<int:workspace_id>/dashboard/", DashboardView.as_view()),
]
