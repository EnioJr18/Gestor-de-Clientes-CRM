from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import CSRFCheck, SessionAuthentication
from rest_framework.exceptions import PermissionDenied


class ApiSessionAuthentication(SessionAuthentication):
    def authenticate_header(self, request):
        return "Session"


class PublicAuthEndpointAuthentication:
    """Nao autentica endpoints publicos, mas preserva o challenge HTTP 401."""

    def authenticate(self, request):
        return None

    def authenticate_header(self, request):
        return "Bearer"


class ApiSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.accounts.api.authentication.ApiSessionAuthentication"
    name = "SessionAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
            "description": "Sessao Django. Escritas autenticadas por sessao exigem CSRF.",
        }


def enforce_csrf(request):
    django_request = request._request
    check = CSRFCheck(lambda req: None)
    check.process_request(django_request)
    reason = check.process_view(django_request, None, (), {})
    if reason:
        raise PermissionDenied("CSRF ausente ou invalido.", code="csrf_failed")
