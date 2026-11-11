from django.conf import settings
from django.db import models


class Workspace(models.Model):
    """Espacio de trabajo aislado: cada usuario tiene uno por tipo."""

    class Kind(models.TextChoices):
        PERSONAL = "personal", "Personal"
        UNIVERSITARIO = "universitario", "Universitario"
        NEGOCIO = "negocio", "Negocio"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspaces")
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "kind"], name="unique_workspace_kind_per_owner"),
        ]

    def __str__(self):
        return f"{self.name} ({self.kind})"
