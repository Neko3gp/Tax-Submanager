from django.urls import path

from .views import ExpenseViewSet

expense_list = ExpenseViewSet.as_view({"get": "list", "post": "create"})
expense_detail = ExpenseViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("workspaces/<int:workspace_id>/expenses/", expense_list),
    path("workspaces/<int:workspace_id>/expenses/<int:pk>/", expense_detail),
]
