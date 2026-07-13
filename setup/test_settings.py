import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from setup.settings.base import env_bool


BASE_ENV = {
    "CRM_LOAD_DOTENV": "0",
    "PYTHONPATH": str(Path(__file__).resolve().parents[1]),
}


def import_settings(module, extra_env=None):
    env = os.environ.copy()
    env.update(BASE_ENV)
    env.pop("SECRET_KEY", None)
    env.pop("DATABASE_URL", None)
    env.pop("ALLOWED_HOSTS", None)
    env.pop("DEBUG", None)
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
        result = import_settings("setup.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY e obrigatoria", result.stderr)

    def test_rejects_empty_secret_key(self):
        env = {**self.valid_env, "SECRET_KEY": " "}
        result = import_settings("setup.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY e obrigatoria", result.stderr)

    def test_requires_database_url(self):
        env = self.valid_env.copy()
        env.pop("DATABASE_URL")
        result = import_settings("setup.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL e obrigatoria", result.stderr)

    def test_requires_allowed_hosts(self):
        env = self.valid_env.copy()
        env.pop("ALLOWED_HOSTS")
        result = import_settings("setup.settings.production", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS e obrigatoria", result.stderr)

    def test_rejects_wildcard_allowed_hosts(self):
        result = import_settings("setup.settings.production", {**self.valid_env, "ALLOWED_HOSTS": "*"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS=* nao e permitido", result.stderr)

    def test_rejects_debug_true(self):
        result = import_settings("setup.settings.production", {**self.valid_env, "DEBUG": "True"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DEBUG nao pode ser True", result.stderr)

    def test_valid_environment_imports(self):
        result = import_settings("setup.settings.production", self.valid_env)
        self.assertEqual(result.returncode, 0, result.stderr)


class EnvironmentSettingsTests(SimpleTestCase):
    def test_development_defaults_to_sqlite_and_http(self):
        from setup.settings import development

        self.assertEqual(development.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")
        self.assertIn("127.0.0.1", development.ALLOWED_HOSTS)
        self.assertFalse(development.SESSION_COOKIE_SECURE)
        self.assertFalse(development.CSRF_COOKIE_SECURE)
        self.assertFalse(development.SECURE_SSL_REDIRECT)

    def test_test_settings_are_isolated(self):
        from setup.settings import test

        self.assertEqual(test.SECRET_KEY, "test-only-secret-key")
        self.assertFalse(test.DEBUG)
        self.assertIn("testserver", test.ALLOWED_HOSTS)
        self.assertEqual(test.DATABASES["default"]["TEST"]["NAME"], ":memory:")
