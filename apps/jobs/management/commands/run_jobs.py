import subprocess
import sys
from time import monotonic

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.jobs.services import claim, finish


class Command(BaseCommand):
    help = "Process a finite batch of due jobs."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--seconds", type=int, default=60)

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 100 or not 1 <= options["seconds"] <= 600:
            raise CommandError("Limit must be 1–100 and duration 1–600 seconds.")
        deadline = monotonic() + options["seconds"]
        handled = 0
        for _ in range(options["limit"]):
            if deadline - monotonic() < 1:
                break
            job = claim()
            if job is None:
                break
            error = self.execute_job(job, deadline)
            finish(job, error=error)
            handled += 1
        self.stdout.write(f"Processed {handled} job claims.")

    @staticmethod
    def execute_job(job, deadline):
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(settings.BASE_DIR / "manage.py"),
                    "execute_job",
                    str(job.pk),
                    str(job.lease_token),
                    f"--settings={settings.SETTINGS_MODULE}",
                ],
                timeout=max(0.1, min(job.timeout_seconds, deadline - monotonic())),
                check=False,
                stdout=None if settings.DEBUG else subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return "timeout"
        except OSError:
            return "handler_failed"
        if result.returncode == 0:
            return ""
        return "handler_missing" if result.returncode == 3 else "handler_failed"
