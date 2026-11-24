import uuid

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.catalogue.services import public_items
from apps.integrations.commons_images import import_commons_image
from apps.integrations.http import ProviderUnavailable


class Command(BaseCommand):
    help = "Import display metadata for a reviewed Wikimedia Commons file."

    def add_arguments(self, parser):
        parser.add_argument("item_id", type=uuid.UUID)
        parser.add_argument("filename")
        parser.add_argument("description")
        parser.add_argument("--rights-reviewed", action="store_true")

    def handle(self, *args, **options):
        if not options["rights_reviewed"]:
            raise CommandError(
                "Review the Commons file and its terms before importing."
            )
        item = public_items().filter(public_id=options["item_id"]).first()
        if item is None:
            raise CommandError("Select a public catalogue item.")
        try:
            import_commons_image(item, options["filename"], options["description"])
        except (ValidationError, ProviderUnavailable) as error:
            raise CommandError(str(error)) from None
        self.stdout.write("Imported the image reference and attribution.")
