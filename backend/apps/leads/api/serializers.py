from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.leads.models import Lead


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
