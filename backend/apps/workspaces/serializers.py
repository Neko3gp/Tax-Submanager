from rest_framework import serializers

from .models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "name", "kind", "monthly_budget"]
        read_only_fields = ["id", "kind"]

    def validate_monthly_budget(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El presupuesto no puede ser negativo.")
        return value
