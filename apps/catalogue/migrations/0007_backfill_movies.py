from django.db import migrations


def backfill_movies(apps, schema_editor):
    Movie = apps.get_model("catalogue", "Movie")
    Item = apps.get_model("catalogue", "CatalogueItem")
    Job = apps.get_model("jobs", "BackgroundJob")
    database = schema_editor.connection.alias
    films = Item.objects.using(database).filter(kind="movie")
    for item_id in films.values_list("id", flat=True).iterator(chunk_size=500):
        Movie.objects.using(database).get_or_create(item_id=item_id)
    eligible = films.filter(
        is_public=True, owner__isnull=True, external_ids__namespace="wikidata"
    )
    for item_id in (
        eligible.values_list("pk", flat=True).distinct().iterator(chunk_size=500)
    ):
        Job.objects.using(database).get_or_create(
            dedup_key=f"enrich-screen:{item_id}",
            defaults={"kind": "enrich-screen", "object_id": item_id},
        )


class Migration(migrations.Migration):
    dependencies = [("catalogue", "0006_movie")]
    operations = [migrations.RunPython(backfill_movies, migrations.RunPython.noop)]
