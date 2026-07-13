from rest_framework.authentication import SessionAuthentication
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class ApiSessionAuthentication(SessionAuthentication):
    def authenticate_header(self, request):
        return "Session"


class ApiSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.leads.api.authentication.ApiSessionAuthentication"
    name = "SessionAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
            "description": "Autenticacao por sessao Django. Escritas autenticadas exigem CSRF.",
        }
