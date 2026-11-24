from django.db import migrations


def backfill_tv_shows(apps, schema_editor):
    Show = apps.get_model("catalogue", "TVShow")
    CatalogueItem = apps.get_model("catalogue", "CatalogueItem")
    Job = apps.get_model("jobs", "BackgroundJob")
    database = schema_editor.connection.alias
    items = CatalogueItem.objects.using(database).filter(kind="tv-show")
    for item_id in items.values_list("pk", flat=True).iterator(chunk_size=500):
        Show.objects.using(database).get_or_create(item_id=item_id)
    eligible = items.filter(
        is_public=True, owner__isnull=True, external_ids__namespace="wikidata"
    )
    for item_id in (
        eligible.values_list("pk", flat=True).distinct().iterator(chunk_size=500)
    ):
        Job.objects.using(database).get_or_create(
            dedup_key=f"enrich-tv:{item_id}",
            defaults={"kind": "enrich-tv", "object_id": item_id},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0008_tvepisode_tvseason_tvshow_tvshowcharacter_and_more")
    ]
    operations = [migrations.RunPython(backfill_tv_shows, migrations.RunPython.noop)]
