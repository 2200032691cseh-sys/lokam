import uuid

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from apps.jobs.services import active_lease


class Command(BaseCommand):
    help = "Execute one leased job in a supervised subprocess."

    def add_arguments(self, parser):
        parser.add_argument("job_id", type=uuid.UUID)
        parser.add_argument("lease_token", type=uuid.UUID)

    def handle(self, *args, **options):
        job = active_lease(options["job_id"], options["lease_token"]).first()
        if job is None:
            raise CommandError("Job lease is unavailable.")
        handler = settings.LOKAM_JOB_HANDLERS.get(job.kind)
        if handler is None:
            raise CommandError("No handler is configured.", returncode=3)
        try:
            import_string(handler)(job)
        except Exception:
            raise CommandError("Job handler failed.") from None
