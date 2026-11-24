from django.core.management.base import BaseCommand, CommandError

from apps.catalogue.models import ItemKind
from apps.integrations.adapters import search_external
from apps.integrations.http import ProviderUnavailable

SMOKE_QUERIES = {
    ItemKind.BOOK: "Pride and Prejudice",
    ItemKind.MOVIE: "Pride and Prejudice",
    ItemKind.SHOW: "Pride and Prejudice",
}


class Command(BaseCommand):
    help = "Verify a live provider read without saving external metadata."

    def add_arguments(self, parser):
        parser.add_argument("kind", choices=SMOKE_QUERIES)

    def handle(self, *args, **options):
        kind = options["kind"]
        try:
            matches = search_external(kind, SMOKE_QUERIES[kind])
        except ProviderUnavailable as error:
            raise CommandError(str(error)) from None
        if not matches:
            raise CommandError("No valid matches for the verification query.")
        self.stdout.write(f"Verified live {matches[0].provider} response for {kind}.")
