from django.urls import path

from .views import BackupListCreateView, BackupRestoreView

urlpatterns = [
    path("backups/", BackupListCreateView.as_view()),
    path("backups/<str:name>/restore/", BackupRestoreView.as_view()),
]
