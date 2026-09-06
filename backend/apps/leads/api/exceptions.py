from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler


DEFAULT_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: ("validation_error", "Os dados enviados sao invalidos."),
    status.HTTP_401_UNAUTHORIZED: ("not_authenticated", "Autenticacao obrigatoria."),
    status.HTTP_403_FORBIDDEN: ("permission_denied", "Voce nao tem permissao para executar esta acao."),
    status.HTTP_404_NOT_FOUND: ("not_found", "Recurso nao encontrado."),
    status.HTTP_405_METHOD_NOT_ALLOWED: ("method_not_allowed", "Metodo nao permitido."),
    status.HTTP_409_CONFLICT: ("conflict", "A requisicao conflita com o estado atual do recurso."),
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: ("unsupported_media_type", "Tipo de conteudo nao suportado."),
    status.HTTP_429_TOO_MANY_REQUESTS: ("throttled", "Muitas requisicoes."),
}


def _flatten_errors(data):
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"non_field_errors": data}
    if data in (None, ""):
        return {}
    return {"detail": [str(data)]}


def _payload(http_status, *, code=None, message=None, errors=None):
    default_code, default_message = DEFAULT_MESSAGES.get(
        http_status,
        ("server_error", "Erro interno do servidor."),
    )
    return {
        "status": http_status,
        "code": code or default_code,
        "message": message or default_message,
        "errors": errors or {},
    }


def api_exception_handler(exc, context):
    if isinstance(exc, IntegrityError):
        return Response(
            _payload(
                status.HTTP_409_CONFLICT,
                errors={"non_field_errors": ["A restricao de integridade do banco foi violada."]},
            ),
            status=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, DjangoValidationError):
        errors = getattr(exc, "message_dict", None) or {"non_field_errors": exc.messages}
        return Response(
            _payload(status.HTTP_400_BAD_REQUEST, errors=errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, exceptions.ValidationError):
        response.data = _payload(status.HTTP_400_BAD_REQUEST, errors=_flatten_errors(response.data))
        return response

    if isinstance(exc, exceptions.AuthenticationFailed):
        code = "authentication_failed"
        message = "Autenticacao falhou."
        exc_codes = exc.get_codes()
        if exc_codes == "invalid_credentials":
            message = "Credenciais invalidas."
        elif exc_codes == "refresh_missing":
            message = "Refresh token ausente."
        elif exc_codes == "invalid_refresh":
            message = "Refresh token invalido, expirado ou revogado."
        else:
            message = "Token invalido ou expirado."
        response.data = _payload(status.HTTP_401_UNAUTHORIZED, code=code, message=message)
        response.data["errors"] = None
        return response

    if isinstance(exc, exceptions.PermissionDenied) and exc.get_codes() == "csrf_failed":
        response.data = _payload(
            status.HTTP_403_FORBIDDEN,
            code="csrf_failed",
            message="CSRF ausente ou invalido.",
        )
        response.data["errors"] = None
        return response

    if isinstance(exc, Http404):
        response.data = _payload(status.HTTP_404_NOT_FOUND)
        return response

    http_status = response.status_code
    errors = {}
    detail = response.data.get("detail") if isinstance(response.data, dict) else response.data
    if detail and http_status == status.HTTP_405_METHOD_NOT_ALLOWED:
        errors = {"detail": [str(detail)]}

    response.data = _payload(http_status, errors=errors)
    return response
