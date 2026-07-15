from django.core.exceptions import ImproperlyConfigured

from .base import BASE_DIR, database_url_config, env_bool, env_bool_or_default, env_list, env_origins
from .base import *  # noqa: F403


SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "development-only-secret-key-change-me",
)

DEBUG = env_bool_or_default("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])
CORS_ALLOWED_ORIGINS = env_origins("CORS_ALLOWED_ORIGINS", [])
CSRF_TRUSTED_ORIGINS = env_origins("CSRF_TRUSTED_ORIGINS", [])
if JWT_REFRESH_COOKIE_SAMESITE == "None" and not JWT_REFRESH_COOKIE_SECURE:  # noqa: F405
    raise ImproperlyConfigured("SameSite=None exige JWT_REFRESH_COOKIE_SECURE=True.")

if env_bool("USE_SQLITE", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": database_url_config(
            "DATABASE_URL",
            conn_max_age=int(os.environ.get("DATABASE_CONN_MAX_AGE", "60")),
            conn_health_checks=True,
            require_postgresql=True,
        )
    }

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
