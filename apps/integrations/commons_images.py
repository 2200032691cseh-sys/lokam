import html
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.html import strip_tags

from apps.catalogue.models import SourceProvider
from apps.catalogue.services import record_source
from apps.media.licences import COMMONS_LICENCE_LINKS
from apps.media.services import record_catalogue_image

from .http import get_json


def _metadata(mapping, key):
    value = (
        mapping.get(key, {}).get("value", "")
        if isinstance(mapping.get(key), dict)
        else ""
    )
    return html.unescape(strip_tags(value)).strip() if isinstance(value, str) else ""


def import_commons_image(item, filename, description, *, fetch=get_json):
    if (
        not filename.startswith("File:")
        or not 6 <= len(filename) <= 140
        or "|" in filename
    ):
        raise ValidationError("Provide one Wikimedia Commons file title.")
    result = fetch(
        "commons-image",
        "/w/api.php",
        params={
            "action": "query",
            "titles": filename,
            "prop": "imageinfo",
            "iiprop": "url|mime|timestamp|extmetadata",
            "iiurlwidth": 480,
            "iiextmetadatafilter": "LicenseShortName|Artist|Attribution|Restrictions",
            "format": "json",
            "formatversion": 2,
        },
        headers={"User-Agent": "Lokam/0.1"},
    )
    try:
        info = result["query"]["pages"][0]["imageinfo"][0]
        metadata = info["extmetadata"]
        url = info["thumburl"]
        source_url = info["descriptionurl"]
        revision = info["timestamp"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValidationError(
            "The source did not supply complete image rights metadata."
        ) from error
    if not isinstance(metadata, dict) or info.get("mime") not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        raise ValidationError("Use a licensed JPEG, PNG or WebP image.")
    licence = _metadata(metadata, "LicenseShortName")
    credit = _metadata(metadata, "Attribution") or _metadata(metadata, "Artist")
    if (
        licence not in COMMONS_LICENCE_LINKS
        or _metadata(metadata, "Restrictions")
        or not credit
    ):
        raise ValidationError("This artwork needs a separate rights review.")
    try:
        parts = urlsplit(url)
        parameters = parse_qsl(parts.query, max_num_fields=8)
    except (TypeError, ValueError) as error:
        raise ValidationError("The Commons thumbnail URL is invalid.") from error
    tracking = {"utm_source", "utm_campaign", "utm_content"}
    if any(key not in tracking for key, _ in parameters):
        raise ValidationError(
            "The Commons thumbnail URL includes unsupported parameters."
        )
    url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    with transaction.atomic():
        source = record_source(
            item,
            provider=SourceProvider.WIKIMEDIA,
            reference=filename,
            revision=revision,
            url=source_url,
            fields={"image"},
            licence=licence,
            show_credit=True,
        )
        return record_catalogue_image(
            source,
            url=url,
            licence=licence,
            credit=" ".join(credit.split())[:240],
            description=description,
        )
