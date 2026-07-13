from .base import BASE_DIR, database_from_url, env_bool, env_bool_or_default, env_list
from .base import *  # noqa: F403


SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "development-only-secret-key-change-me",
)

DEBUG = env_bool_or_default("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", [])

if env_bool("USE_DATABASE_URL", False) and os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": database_from_url(os.environ["DATABASE_URL"]),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
