from django.urls import path

from . import views

urlpatterns = [
    path("workspaces/", views.WorkspaceListView.as_view()),
    path("workspaces/<int:pk>/", views.WorkspaceDetailView.as_view()),
    path("categories/", views.categories),
]
