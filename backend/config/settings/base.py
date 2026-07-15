import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = BACKEND_DIR.parent
BASE_DIR = BACKEND_DIR

if os.environ.get("CRM_LOAD_DOTENV", "1").strip().lower() not in {"0", "false", "no", "off"}:
    load_dotenv(REPOSITORY_ROOT / ".env")


def env_bool(name, default=None, *, required=False):
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        if required:
            raise ImproperlyConfigured(f"{name} e obrigatoria neste ambiente.")
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(
        f"{name} deve ser um booleano valido: 1, true, yes, on, 0, false, no ou off."
    )


def env_bool_or_default(name, default):
    try:
        return env_bool(name, default)
    except ImproperlyConfigured:
        return default


def env_list(name, default=None, *, required=False):
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        if required:
            raise ImproperlyConfigured(f"{name} e obrigatoria neste ambiente.")
        return list(default or [])

    items = []
    seen = set()
    for item in value.split(","):
        normalized = item.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            items.append(normalized)
    if required and not items:
        raise ImproperlyConfigured(f"{name} deve conter ao menos um valor.")
    return items


def env_origins(name, default=None, *, required=False):
    origins = env_list(name, default, required=required)
    for origin in origins:
        parsed = urlparse(origin)
        if (
            "*" in origin
            or parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.path
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            raise ImproperlyConfigured(
                f"{name} deve conter apenas origens HTTP(S) explicitas, com esquema e host."
            )
    return origins


def required_env(name):
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        raise ImproperlyConfigured(f"{name} e obrigatoria neste ambiente.")
    return value.strip()


def database_from_url(url, *, conn_max_age=0, conn_health_checks=False):
    return dj_database_url.parse(
        url,
        conn_max_age=conn_max_age,
        conn_health_checks=conn_health_checks,
    )


def database_url_config(name, *, conn_max_age=0, conn_health_checks=False, require_postgresql=False):
    url = required_env(name)
    config = database_from_url(
        url,
        conn_max_age=conn_max_age,
        conn_health_checks=conn_health_checks,
    )
    if require_postgresql and config["ENGINE"] != "django.db.backends.postgresql":
        raise ImproperlyConfigured(f"{name} deve usar PostgreSQL.")
    return config


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "apps.accounts.apps.AccountsConfig",
    "apps.leads.apps.LeadsConfig",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "static")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_URL = "/login/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "apps.accounts.api.authentication.ApiSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.leads.api.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.leads.api.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "auth_login": os.environ.get("JWT_LOGIN_THROTTLE_RATE", "5/min"),
        "auth_refresh": os.environ.get("JWT_REFRESH_THROTTLE_RATE", "20/min"),
        "auth_csrf": os.environ.get("JWT_CSRF_THROTTLE_RATE", "60/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

JWT_REFRESH_COOKIE_NAME = os.environ.get("JWT_REFRESH_COOKIE_NAME", "crm_refresh")
JWT_REFRESH_COOKIE_SAMESITE = os.environ.get("JWT_REFRESH_COOKIE_SAMESITE", "Lax")
if JWT_REFRESH_COOKIE_SAMESITE not in {"Lax", "Strict", "None"}:
    raise ImproperlyConfigured("JWT_REFRESH_COOKIE_SAMESITE deve ser Lax, Strict ou None.")
JWT_REFRESH_COOKIE_SECURE = env_bool("JWT_REFRESH_COOKIE_SECURE", False)
JWT_REFRESH_COOKIE_DOMAIN = os.environ.get("JWT_REFRESH_COOKIE_DOMAIN", "").strip() or None
JWT_REFRESH_COOKIE_PATH = os.environ.get("JWT_REFRESH_COOKIE_PATH", "/api/v1/auth/")
if not JWT_REFRESH_COOKIE_PATH.startswith("/"):
    raise ImproperlyConfigured("JWT_REFRESH_COOKIE_PATH deve iniciar com /.")
CORS_ALLOWED_ORIGINS = env_origins("CORS_ALLOWED_ORIGINS", [])
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/api/.*$"

SPECTACULAR_SETTINGS = {
    "TITLE": "CRM.Pro API",
    "DESCRIPTION": "API REST v1 para leads do CRM.Pro.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "CRM.Pro <no-reply@example.com>")
