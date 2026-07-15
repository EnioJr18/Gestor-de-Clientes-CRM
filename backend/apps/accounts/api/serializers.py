from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class StrictFieldsMixin:
    def to_internal_value(self, data):
        if not hasattr(data, "keys"):
            raise serializers.ValidationError({"non_field_errors": ["Objeto JSON invalido."]})
        unknown = set(data.keys()) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {field: ["Campo desconhecido."] for field in sorted(unknown)}
            )
        return super().to_internal_value(data)


class LoginSerializer(StrictFieldsMixin, serializers.Serializer):
    username = serializers.CharField(trim_whitespace=True, allow_blank=False)
    password = serializers.CharField(trim_whitespace=False, allow_blank=False, write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None or not user.is_active:
            raise AuthenticationFailed("Credenciais invalidas.", code="invalid_credentials")
        attrs["user"] = user
        return attrs


class EmptyPayloadSerializer(StrictFieldsMixin, serializers.Serializer):
    pass


class SafeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]
        read_only_fields = fields


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = SafeUserSerializer()


class AccessResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()


class CsrfResponseSerializer(serializers.Serializer):
    csrfToken = serializers.CharField()
