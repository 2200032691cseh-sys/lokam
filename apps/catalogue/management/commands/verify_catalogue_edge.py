from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.catalogue.models import CatalogueRelationship
from apps.catalogue.relationships import verify_edge


class Command(BaseCommand):
    help = "Mark a catalogue relationship verified after reviewing its evidence and endpoints."

    def add_arguments(self, parser):
        parser.add_argument("edge_id", type=int)
        parser.add_argument("--reviewed", action="store_true")

    def handle(self, *args, **options):
        if not options["reviewed"]:
            raise CommandError("Review the evidence before passing --reviewed.")
        try:
            edge = verify_edge(options["edge_id"])
        except (CatalogueRelationship.DoesNotExist, ValidationError):
            raise CommandError(
                "The relationship has no eligible evidence or does not exist."
            ) from None
        self.stdout.write(f"Verified catalogue relationship {edge.pk}.")
