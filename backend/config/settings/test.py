from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urlparse

from .base import BASE_DIR, database_url_config, env_bool, env_list
from .base import *  # noqa: F403


SECRET_KEY = "test-only-secret-key-with-at-least-thirty-two-bytes-for-hs256"
DEBUG = False
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["testserver", "127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = []
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]

if env_bool("USE_SQLITE_FOR_TESTS", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test.sqlite3",
            "TEST": {
                "NAME": ":memory:",
            },
        }
    }
else:
    DATABASES = {
        "default": database_url_config(
            "TEST_DATABASE_URL",
            conn_max_age=0,
            conn_health_checks=True,
            require_postgresql=True,
        )
    }
    default_name = DATABASES["default"].get("NAME")
    production_name = urlparse(os.environ.get("DATABASE_URL", "")).path.lstrip("/")
    if production_name and default_name == production_name:
        raise ImproperlyConfigured("TEST_DATABASE_URL nao pode apontar para o banco de desenvolvimento/producao.")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
JWT_REFRESH_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
