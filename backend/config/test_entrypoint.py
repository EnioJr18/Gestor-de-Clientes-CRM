import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENTRYPOINT = BACKEND_DIR / "entrypoint.sh"


@unittest.skipUnless(shutil.which("sh"), "Requer um shell POSIX para validar o entrypoint.")
class EntrypointTests(unittest.TestCase):
    def run_entrypoint(self, migration_exit_code):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            bin_path = temporary_path / "bin"
            bin_path.mkdir()
            invocation_log = temporary_path / "invocations.log"

            (bin_path / "python").write_text(
                "#!/bin/sh\nprintf 'python %s\\n' \"$*\" >> \"$ENTRYPOINT_TEST_LOG\"\n"
                f"exit {migration_exit_code}\n",
                encoding="ascii",
            )
            (bin_path / "gunicorn").write_text(
                "#!/bin/sh\nprintf 'gunicorn %s\\n' \"$*\" >> \"$ENTRYPOINT_TEST_LOG\"\n",
                encoding="ascii",
            )
            for command in bin_path.iterdir():
                command.chmod(0o755)

            secret_marker = "secret-value-that-must-not-appear-in-output"
            environment = {
                **os.environ,
                "PATH": f"{bin_path}{os.pathsep}{os.environ['PATH']}",
                "ENTRYPOINT_TEST_LOG": str(invocation_log),
                "PORT": "9123",
                "SECRET_KEY": secret_marker,
            }
            result = subprocess.run(
                ["sh", str(ENTRYPOINT)],
                cwd=temporary_path,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            invocations = invocation_log.read_text(encoding="ascii") if invocation_log.exists() else ""
            return result, invocations, secret_marker

    def test_migration_failure_prevents_gunicorn_startup(self):
        result, invocations, secret_marker = self.run_entrypoint(migration_exit_code=41)

        self.assertEqual(result.returncode, 41)
        self.assertIn(
            "python /app/manage.py migrate --noinput --settings=config.settings.production",
            invocations,
        )
        self.assertNotIn("gunicorn ", invocations)
        self.assertNotIn(secret_marker, result.stdout)
        self.assertNotIn(secret_marker, result.stderr)

    def test_successful_migration_executes_gunicorn_with_current_arguments(self):
        result, invocations, secret_marker = self.run_entrypoint(migration_exit_code=0)

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "python /app/manage.py migrate --noinput --settings=config.settings.production",
            invocations,
        )
        self.assertIn(
            "gunicorn config.wsgi:application --bind 0.0.0.0:9123 --workers 2 "
            "--access-logfile - --error-logfile -",
            invocations,
        )
        self.assertNotIn(secret_marker, result.stdout)
        self.assertNotIn(secret_marker, result.stderr)
