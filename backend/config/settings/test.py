from .base import BASE_DIR, env_list
from .base import *  # noqa: F403


SECRET_KEY = "test-only-secret-key"
DEBUG = False
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["testserver", "127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",
        "TEST": {
            "NAME": ":memory:",
        },
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
