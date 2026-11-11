from django.db import models


class Expense(models.Model):
    """Pago periódico registrado dentro de un espacio de trabajo."""

    class Frequency(models.TextChoices):
        MONTHLY = "mensual", "Mensual"
        YEARLY = "anual", "Anual"

    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="expenses")
    name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    cut_date = models.DateField()
    category = models.CharField(max_length=60)
    frequency = models.CharField(max_length=10, choices=Frequency.choices, default=Frequency.MONTHLY)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cut_date", "id"]

    def __str__(self):
        return f"{self.name} (${self.amount})"
