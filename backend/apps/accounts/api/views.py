from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import PublicAuthEndpointAuthentication, enforce_csrf
from .cookies import delete_refresh_cookie, get_refresh_cookie, set_refresh_cookie
from .serializers import (
    AccessResponseSerializer,
    ChangePasswordSerializer,
    CsrfResponseSerializer,
    EmptyPayloadSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    RegistrationSerializer,
    SafeUserSerializer,
    UserProfileSerializer,
)
from .throttles import CsrfRateThrottle, LoginRateThrottle, RefreshRateThrottle, RegistrationRateThrottle


REFRESH_COOKIE_PARAMETER = OpenApiParameter(
    name="crm_refresh",
    type=str,
    location=OpenApiParameter.COOKIE,
    required=True,
    description="Refresh token em cookie HttpOnly; o nome real e configuravel.",
)
CSRF_HEADER_PARAMETER = OpenApiParameter(
    name="X-CSRFToken",
    type=str,
    location=OpenApiParameter.HEADER,
    required=True,
    description="Token obtido em GET /api/v1/auth/csrf/ e pareado ao cookie csrftoken.",
)


def token_payload(access):
    return {
        "access": access,
        "token_type": "Bearer",
        "expires_in": int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(APIView):
    authentication_classes = [PublicAuthEndpointAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [CsrfRateThrottle]

    @extend_schema(auth=[], responses={200: CsrfResponseSerializer})
    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(APIView):
    authentication_classes = [PublicAuthEndpointAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    # JSON forces a CORS preflight, preventing a cross-site HTML form from issuing login requests.
    parser_classes = [JSONParser]

    @extend_schema(
        auth=[],
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(description="Payload invalido."),
            401: OpenApiResponse(description="Credenciais invalidas."),
            415: OpenApiResponse(description="O login aceita somente JSON."),
            429: OpenApiResponse(description="Limite de tentativas excedido."),
        },
        examples=[OpenApiExample("Login", value={"username": "usuario", "password": "senha"}, request_only=True)],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response = Response(
            {**token_payload(str(refresh.access_token)), "user": SafeUserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
        return set_refresh_cookie(response, str(refresh))


class RefreshView(APIView):
    authentication_classes = [PublicAuthEndpointAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [RefreshRateThrottle]

    @extend_schema(
        auth=[],
        request=EmptyPayloadSerializer,
        parameters=[REFRESH_COOKIE_PARAMETER, CSRF_HEADER_PARAMETER],
        responses={
            200: AccessResponseSerializer,
            400: OpenApiResponse(description="Payload invalido."),
            401: OpenApiResponse(description="Refresh ausente, invalido, expirado ou revogado."),
            403: OpenApiResponse(description="CSRF ausente ou invalido."),
            429: OpenApiResponse(description="Limite de refresh excedido."),
        },
    )
    def post(self, request):
        enforce_csrf(request)
        payload = EmptyPayloadSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        raw_refresh = get_refresh_cookie(request)
        if not raw_refresh:
            raise AuthenticationFailed("Refresh token ausente.", code="refresh_missing")
        serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, AuthenticationFailed, ObjectDoesNotExist) as exc:
            raise AuthenticationFailed(
                "Refresh token invalido, expirado ou revogado.", code="invalid_refresh"
            ) from exc
        response = Response(token_payload(serializer.validated_data["access"]))
        return set_refresh_cookie(response, serializer.validated_data["refresh"])


class LogoutView(APIView):
    authentication_classes = [PublicAuthEndpointAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        auth=[],
        request=EmptyPayloadSerializer,
        parameters=[REFRESH_COOKIE_PARAMETER, CSRF_HEADER_PARAMETER],
        responses={204: None, 400: OpenApiResponse(description="Payload invalido."), 403: OpenApiResponse(description="CSRF ausente ou invalido.")},
    )
    def post(self, request):
        enforce_csrf(request)
        payload = EmptyPayloadSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        raw_refresh = get_refresh_cookie(request)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass
        return delete_refresh_cookie(Response(status=status.HTTP_204_NO_CONTENT))


class RegistrationView(APIView):
    authentication_classes = [PublicAuthEndpointAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]
    parser_classes = [JSONParser]

    @extend_schema(
        auth=[],
        request=RegistrationSerializer,
        responses={
            201: SafeUserSerializer,
            400: OpenApiResponse(description="Payload invalido."),
            415: OpenApiResponse(description="O cadastro aceita somente JSON."),
            429: OpenApiResponse(description="Limite de cadastros excedido."),
        },
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(SafeUserSerializer(user).data, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            204: None,
            400: OpenApiResponse(description="Payload invalido."),
            401: OpenApiResponse(description="Autenticacao obrigatoria."),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save(update_fields=["password"])
            for outstanding_token in OutstandingToken.objects.filter(user=request.user):
                BlacklistedToken.objects.get_or_create(token=outstanding_token)

        if request.session.get("_auth_user_id") == str(request.user.pk):
            update_session_auth_hash(request, request.user)
        return delete_refresh_cookie(Response(status=status.HTTP_204_NO_CONTENT))


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: SafeUserSerializer, 401: OpenApiResponse(description="Autenticacao obrigatoria.")})
    def get(self, request):
        return Response(SafeUserSerializer(request.user).data)

    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: SafeUserSerializer,
            400: OpenApiResponse(description="Payload invalido."),
            401: OpenApiResponse(description="Autenticacao obrigatoria."),
        },
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(SafeUserSerializer(user).data)
