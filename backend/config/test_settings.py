import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.settings.base import env_bool


BASE_ENV = {
    "CRM_LOAD_DOTENV": "0",
    "PYTHONPATH": str(Path(__file__).resolve().parents[1]),
}


def import_settings(module, extra_env=None):
    env = os.environ.copy()
    env.update(BASE_ENV)
    env.pop("SECRET_KEY", None)
    env.pop("DATABASE_URL", None)
    env.pop("TEST_DATABASE_URL", None)
    env.pop("ALLOWED_HOSTS", None)
    env.pop("DEBUG", None)
    env.pop("USE_SQLITE", None)
    env.pop("USE_SQLITE_FOR_TESTS", None)
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        [sys.executable, "-c", f"import {module}; print('ok')"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def run_settings_code(module, code, extra_env=None):
    env = os.environ.copy()
    env.update(BASE_ENV)
    env.pop("SECRET_KEY", None)
    env.pop("DATABASE_URL", None)
    env.pop("TEST_DATABASE_URL", None)
    env.pop("ALLOWED_HOSTS", None)
    env.pop("DEBUG", None)
    env.pop("USE_SQLITE", None)
    env.pop("USE_SQLITE_FOR_TESTS", None)
    if extra_env:
        env.update(extra_env)

    script = f"from {module} import *\n{code}"
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class EnvBoolTests(SimpleTestCase):
    def test_true_values(self):
        for value in ["true", "True", " 1 ", "YES", "on"]:
            with self.subTest(value=value), mock.patch.dict(os.environ, {"FLAG": value}):
                self.assertIs(env_bool("FLAG"), True)

    def test_false_values(self):
        for value in ["false", "False", " 0 ", "NO", "off"]:
            with self.subTest(value=value), mock.patch.dict(os.environ, {"FLAG": value}):
                self.assertIs(env_bool("FLAG"), False)

    def test_invalid_value_raises_clear_error(self):
        with mock.patch.dict(os.environ, {"FLAG": "maybe"}):
            with self.assertRaisesMessage(ImproperlyConfigured, "FLAG deve ser um booleano valido"):
                env_bool("FLAG")


class ProductionSettingsTests(SimpleTestCase):
    valid_env = {
        "SECRET_KEY": "prod-secret-key-with-more-than-fifty-randomish-characters-123",
        "DATABASE_URL": "postgres://user:pass@localhost:5432/crmpro?sslmode=require",
        "ALLOWED_HOSTS": "crm.example.com",
        "DEBUG": "False",
    }

    def test_requires_secret_key(self):
        env = self.valid_env.copy()
        env.pop("SECRET_KEY")
        result = import_settings("config.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY e obrigatoria", result.stderr)

    def test_rejects_empty_secret_key(self):
        env = {**self.valid_env, "SECRET_KEY": " "}
        result = import_settings("config.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY e obrigatoria", result.stderr)

    def test_requires_database_url(self):
        env = self.valid_env.copy()
        env.pop("DATABASE_URL")
        result = import_settings("config.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL e obrigatoria", result.stderr)

    def test_rejects_sqlite_database_url(self):
        result = import_settings("config.settings.production", {**self.valid_env, "DATABASE_URL": "sqlite:///db.sqlite3"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL deve usar PostgreSQL", result.stderr)

    def test_requires_sslmode_require(self):
        result = import_settings(
            "config.settings.production",
            {**self.valid_env, "DATABASE_URL": "postgres://user:pass@localhost:5432/crmpro"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sslmode=require", result.stderr)

    def test_requires_allowed_hosts(self):
        env = self.valid_env.copy()
        env.pop("ALLOWED_HOSTS")
        result = import_settings("config.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS e obrigatoria", result.stderr)

    def test_rejects_wildcard_allowed_hosts(self):
        result = import_settings("config.settings.production", {**self.valid_env, "ALLOWED_HOSTS": "*"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS=* nao e permitido", result.stderr)

    def test_rejects_debug_true(self):
        result = import_settings("config.settings.production", {**self.valid_env, "DEBUG": "True"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DEBUG nao pode ser True", result.stderr)

    def test_valid_environment_imports(self):
        result = import_settings("config.settings.production", self.valid_env)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_spa_enabled_requires_explicit_cors_and_csrf_origins(self):
        result = import_settings(
            "config.settings.production",
            {**self.valid_env, "SPA_ENABLED": "True"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CORS_ALLOWED_ORIGINS", result.stderr)

    def test_spa_enabled_accepts_explicit_origins(self):
        result = import_settings(
            "config.settings.production",
            {
                **self.valid_env,
                "SPA_ENABLED": "True",
                "CORS_ALLOWED_ORIGINS": "https://spa.example.com",
                "CSRF_TRUSTED_ORIGINS": "https://spa.example.com",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_cors_wildcard(self):
        result = import_settings(
            "config.settings.production",
            {**self.valid_env, "CORS_ALLOWED_ORIGINS": "*"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("origens HTTP(S) explicitas", result.stderr)

    def test_rejects_cors_wildcard_subdomain_and_path(self):
        for origin in ["https://*.example.com", "https://spa.example.com/path"]:
            with self.subTest(origin=origin):
                result = import_settings(
                    "config.settings.production",
                    {**self.valid_env, "CORS_ALLOWED_ORIGINS": origin},
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("origens HTTP(S) explicitas", result.stderr)

    def test_production_rejects_insecure_refresh_cookie(self):
        result = import_settings(
            "config.settings.production",
            {**self.valid_env, "JWT_REFRESH_COOKIE_SECURE": "False"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JWT_REFRESH_COOKIE_SECURE deve ser True", result.stderr)


class EnvironmentSettingsTests(SimpleTestCase):
    def test_development_requires_database_url_by_default(self):
        result = import_settings("config.settings.development")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL e obrigatoria", result.stderr)

    def test_development_uses_postgresql_database_url(self):
        result = import_settings(
            "config.settings.development",
            {"DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_development_rejects_sqlite_database_url_by_default(self):
        result = import_settings("config.settings.development", {"DATABASE_URL": "sqlite:///db.sqlite3"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL deve usar PostgreSQL", result.stderr)

    def test_development_sqlite_requires_explicit_opt_in(self):
        result = import_settings("config.settings.development", {"USE_SQLITE": "True"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_development_http_security_defaults(self):
        result = run_settings_code(
            "config.settings.development",
            "print(SESSION_COOKIE_SECURE); print(CSRF_COOKIE_SECURE); print(SECURE_SSL_REDIRECT); print(','.join(ALLOWED_HOSTS))",
            {"DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("False\nFalse\nFalse", result.stdout)
        self.assertIn("127.0.0.1", result.stdout)

    def test_development_defaults_to_explicit_vite_origin(self):
        result = run_settings_code(
            "config.settings.development",
            "print(','.join(CORS_ALLOWED_ORIGINS)); print(','.join(CSRF_TRUSTED_ORIGINS))",
            {"DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("http://localhost:5173"), 2)

    def test_test_settings_require_test_database_url_by_default(self):
        result = import_settings("config.settings.test")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TEST_DATABASE_URL e obrigatoria", result.stderr)

    def test_test_settings_use_isolated_postgresql_database(self):
        result = import_settings(
            "config.settings.test",
            {
                "DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro",
                "TEST_DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro_test",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_test_settings_reject_development_database_name(self):
        result = import_settings(
            "config.settings.test",
            {
                "DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro",
                "TEST_DATABASE_URL": "postgres://user:pass@localhost:5432/crm_pro",
            },
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TEST_DATABASE_URL nao pode apontar", result.stderr)

    def test_test_settings_sqlite_requires_explicit_opt_in(self):
        result = import_settings("config.settings.test", {"USE_SQLITE_FOR_TESTS": "True"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_test_settings_are_isolated_with_sqlite_opt_in(self):
        result = run_settings_code(
            "config.settings.test",
            "print(SECRET_KEY); print(DEBUG); print(','.join(ALLOWED_HOSTS)); print(DATABASES['default']['TEST']['NAME'])",
            {"USE_SQLITE_FOR_TESTS": "True"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("test-only-secret-key", result.stdout)
        self.assertIn("False", result.stdout)
        self.assertIn("testserver", result.stdout)
        self.assertIn(":memory:", result.stdout)
