from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.integrations.http import ProviderUnavailable
from apps.integrations.wikidata_graph import sync_wikidata_edges


class Command(BaseCommand):
    help = (
        "Import a bounded batch of Wikidata assertions into the catalogue review queue."
    )

    def add_arguments(self, parser):
        parser.add_argument("ids", nargs="+")

    def handle(self, *args, **options):
        try:
            edges = sync_wikidata_edges(options["ids"])
        except (ValidationError, ProviderUnavailable) as error:
            raise CommandError(str(error)) from None
        self.stdout.write(
            f"Recorded evidence on {len({edge.pk for edge in edges})} catalogue relationships."
        )
