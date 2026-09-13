from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()


def normalize_email(value):
    return value.strip().lower()


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


class RegistrationSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    password = serializers.CharField(trim_whitespace=False, allow_blank=False, write_only=True)
    password_confirm = serializers.CharField(trim_whitespace=False, allow_blank=False, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password", "password_confirm"]
        extra_kwargs = {
            "username": {"required": True, "allow_blank": False},
            "email": {"required": True, "allow_blank": False},
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
        }

    def validate_email(self, value):
        return normalize_email(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": ["As senhas nao coincidem."]})

        user = User(
            username=attrs["username"],
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        try:
            validate_password(attrs["password"], user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserProfileSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def validate_email(self, value):
        return normalize_email(value)


class ChangePasswordSerializer(StrictFieldsMixin, serializers.Serializer):
    current_password = serializers.CharField(trim_whitespace=False, allow_blank=False, write_only=True)
    new_password = serializers.CharField(trim_whitespace=False, allow_blank=False, write_only=True)
    new_password_confirm = serializers.CharField(trim_whitespace=False, allow_blank=False, write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": ["Senha atual incorreta."]})
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": ["As senhas nao coincidem."]})
        try:
            validate_password(attrs["new_password"], user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": exc.messages}) from exc
        return attrs


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
