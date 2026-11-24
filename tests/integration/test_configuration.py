import psycopg
from django.conf import settings
from django.core.checks import run_checks


def test_lok_006_django_configuration():
    assert not run_checks()
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"


def test_lok_006_postgresql_connection():
    database = settings.DATABASES["default"]
    with psycopg.connect(
        dbname=database["NAME"],
        user=database["USER"],
        password=database["PASSWORD"],
        host=database["HOST"],
        port=database["PORT"],
        connect_timeout=5,
    ) as connection:
        assert connection.info.server_version // 10_000 == 17
        assert connection.execute("SELECT 1").fetchone() == (1,)
