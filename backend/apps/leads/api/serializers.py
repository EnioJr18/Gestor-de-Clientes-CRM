from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.leads.models import Interaction, Lead


class DashboardPeriodSerializer(serializers.Serializer):
    key = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()


class DashboardMetricsSerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    created_today = serializers.IntegerField()
    created_in_period = serializers.IntegerField()
    converted_in_period = serializers.IntegerField()
    conversion_rate = serializers.FloatField()


class DashboardStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class DashboardPrioritySerializer(serializers.Serializer):
    priority = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class DashboardEvolutionSerializer(serializers.Serializer):
    month = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class DashboardInteractionTypeSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class DashboardRecentLeadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.CharField()
    sobrenome = serializers.CharField(allow_null=True)
    email = serializers.EmailField()
    status = serializers.CharField()
    prioridade = serializers.CharField()
    criado_em = serializers.DateTimeField()


class DashboardSummarySerializer(serializers.Serializer):
    period = DashboardPeriodSerializer()
    metrics = DashboardMetricsSerializer()
    by_status = DashboardStatusSerializer(many=True)
    by_priority = DashboardPrioritySerializer(many=True)
    monthly_evolution = DashboardEvolutionSerializer(many=True)
    recent_leads = DashboardRecentLeadSerializer(many=True)
    interaction_total = serializers.IntegerField()
    interaction_by_type = DashboardInteractionTypeSerializer(many=True)
    leads_with_interaction = serializers.IntegerField()
    leads_without_interaction = serializers.IntegerField()
    interaction_monthly_evolution = DashboardEvolutionSerializer(many=True)


class StrictFieldsMixin:
    protected_fields = set()

    def to_internal_value(self, data):
        if not hasattr(data, "keys"):
            raise serializers.ValidationError({"non_field_errors": ["Objeto JSON invalido."]})

        allowed = set(self.fields)
        received = set(data.keys())
        forbidden = received & self.protected_fields
        unknown = received - allowed
        errors = {}
        for field in sorted(forbidden):
            errors[field] = ["Este campo nao pode ser enviado."]
        for field in sorted(unknown):
            errors[field] = ["Campo desconhecido."]
        if errors:
            raise serializers.ValidationError(errors)
        return super().to_internal_value(data)


class LeadSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    protected_fields = {"id", "agente_responsavel", "criado_em", "atualizado_em"}

    class Meta:
        model = Lead
        fields = [
            "id",
            "nome",
            "sobrenome",
            "email",
            "telefone",
            "status",
            "prioridade",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]
        extra_kwargs = {
            "nome": {"trim_whitespace": True, "allow_blank": False},
            "email": {"trim_whitespace": True, "allow_blank": False},
            "sobrenome": {"trim_whitespace": True, "allow_blank": True, "required": False},
            "telefone": {"trim_whitespace": True, "allow_blank": True, "required": False},
            "status": {"required": False},
            "prioridade": {"required": False},
        }

    def validate_email(self, value):
        email = value.strip().lower()
        request = self.context.get("request")
        owner = getattr(request, "user", None)
        if owner is not None and owner.is_authenticated:
            duplicates = Lead.objects.filter(agente_responsavel=owner, email__iexact=email)
            if self.instance is not None:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise serializers.ValidationError("Ja existe um lead com este e-mail para este usuario.")
        return email

    def validate(self, attrs):
        for field in ("nome", "email"):
            if field in attrs and not attrs[field].strip():
                raise serializers.ValidationError({field: ["Este campo nao pode ficar em branco."]})
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        try:
            with transaction.atomic():
                return Lead.objects.create(agente_responsavel=request.user, **validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"email": ["Ja existe um lead com este e-mail para este usuario."]}
            ) from exc

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                return super().update(instance, validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"email": ["Ja existe um lead com este e-mail para este usuario."]}
            ) from exc


class InteractionSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    protected_fields = {"id", "lead", "criado_em", "atualizado_em"}

    class Meta:
        model = Interaction
        fields = [
            "id",
            "tipo",
            "data_interacao",
            "nota",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]
        extra_kwargs = {
            "tipo": {"required": True},
            "data_interacao": {"required": False},
            "nota": {"trim_whitespace": True, "allow_blank": False},
        }

    def validate_nota(self, value):
        nota = value.strip()
        if not nota:
            raise serializers.ValidationError("Informe uma anotacao.")
        return nota
