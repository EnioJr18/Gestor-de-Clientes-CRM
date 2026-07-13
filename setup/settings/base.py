import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

if os.environ.get("CRM_LOAD_DOTENV", "1").strip().lower() not in {"0", "false", "no", "off"}:
    load_dotenv(BASE_DIR / ".env")


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


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "leads",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "setup.urls"
WSGI_APPLICATION = "setup.wsgi.application"

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

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "CRM.Pro <no-reply@example.com>")
