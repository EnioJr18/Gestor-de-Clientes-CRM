from django.core.exceptions import ImproperlyConfigured

from .base import database_url_config, env_bool, env_list, env_origins, required_env
from .base import *  # noqa: F403


SECRET_KEY = required_env("SECRET_KEY")
if SECRET_KEY.startswith("django-insecure-") or len(set(SECRET_KEY)) < 5 or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "SECRET_KEY de producao deve ser longa, aleatoria e nao pode usar o prefixo django-insecure-."
    )

DEBUG = env_bool("DEBUG", False)
if DEBUG:
    raise ImproperlyConfigured("DEBUG nao pode ser True no ambiente de producao.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", required=True)
if "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS=* nao e permitido no ambiente de producao.")

SPA_ENABLED = env_bool("SPA_ENABLED", False)
CORS_ALLOWED_ORIGINS = env_origins("CORS_ALLOWED_ORIGINS", required=SPA_ENABLED)
CSRF_TRUSTED_ORIGINS = env_origins("CSRF_TRUSTED_ORIGINS", required=SPA_ENABLED)

DATABASES = {
    "default": database_url_config(
        "DATABASE_URL",
        conn_max_age=int(os.environ.get("DATABASE_CONN_MAX_AGE", "600")),
        conn_health_checks=True,
        require_postgresql=True,
    )
}

if DATABASES["default"].get("OPTIONS", {}).get("sslmode") != "require":
    raise ImproperlyConfigured("DATABASE_URL de producao deve exigir sslmode=require.")

MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
JWT_REFRESH_COOKIE_SECURE = env_bool("JWT_REFRESH_COOKIE_SECURE", True)
if not JWT_REFRESH_COOKIE_SECURE:
    raise ImproperlyConfigured("JWT_REFRESH_COOKIE_SECURE deve ser True em producao.")
if JWT_REFRESH_COOKIE_SAMESITE == "None" and not JWT_REFRESH_COOKIE_SECURE:  # noqa: F405
    raise ImproperlyConfigured("SameSite=None exige cookie Secure.")

SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REQUIRE_SHARED_THROTTLE_CACHE = env_bool("REQUIRE_SHARED_THROTTLE_CACHE", False)
LOCAL_CACHE_BACKENDS = {
    "django.core.cache.backends.dummy.DummyCache",
    "django.core.cache.backends.filebased.FileBasedCache",
    "django.core.cache.backends.locmem.LocMemCache",
}
if REQUIRE_SHARED_THROTTLE_CACHE and CACHE_BACKEND in LOCAL_CACHE_BACKENDS:  # noqa: F405
    raise ImproperlyConfigured(
        "CACHE_BACKEND deve usar um cache compartilhado quando REQUIRE_SHARED_THROTTLE_CACHE=True."
    )

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", EMAIL_BACKEND)  # noqa: F405
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", DEFAULT_FROM_EMAIL)  # noqa: F405
