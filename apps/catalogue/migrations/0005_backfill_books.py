from django.db import migrations


def backfill_books(apps, schema_editor):
    CatalogueItem = apps.get_model("catalogue", "CatalogueItem")
    Book = apps.get_model("catalogue", "Book")
    ExternalIdentifier = apps.get_model("catalogue", "ExternalIdentifier")
    BackgroundJob = apps.get_model("jobs", "BackgroundJob")
    database = schema_editor.connection.alias
    book_ids = (
        CatalogueItem.objects.using(database)
        .filter(kind="book")
        .values_list("pk", flat=True)
        .iterator(chunk_size=500)
    )
    for item_id in book_ids:
        Book.objects.using(database).get_or_create(item_id=item_id)
    eligible_ids = (
        ExternalIdentifier.objects.using(database)
        .filter(
            namespace="ol-work",
            item__kind="book",
            item__is_public=True,
            item__owner__isnull=True,
        )
        .values_list("item_id", flat=True)
        .distinct()
        .iterator(chunk_size=500)
    )
    for item_id in eligible_ids:
        BackgroundJob.objects.using(database).get_or_create(
            dedup_key=f"enrich-book:{item_id}",
            defaults={"kind": "enrich-book", "object_id": item_id},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0004_book_bookedition"),
        ("jobs", "0001_initial"),
    ]
    operations = [migrations.RunPython(backfill_books, migrations.RunPython.noop)]
