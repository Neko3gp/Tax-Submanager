import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("cut_date", models.DateField()),
                ("category", models.CharField(max_length=60)),
                (
                    "frequency",
                    models.CharField(
                        choices=[("mensual", "Mensual"), ("anual", "Anual")],
                        default="mensual",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expenses",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={
                "ordering": ["cut_date", "id"],
            },
        ),
    ]
