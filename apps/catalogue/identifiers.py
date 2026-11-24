import re
import uuid
from enum import StrEnum

from django.core.exceptions import ValidationError


class Namespace(StrEnum):
    OPEN_LIBRARY_WORK = "ol-work"
    OPEN_LIBRARY_EDITION = "ol-edition"
    OPEN_LIBRARY_AUTHOR = "ol-author"
    ISBN = "isbn"
    TMDB_MOVIE = "tmdb-movie"
    TMDB_SHOW = "tmdb-show"
    TMDB_PERSON = "tmdb-person"
    TVMAZE_SHOW = "tvmaze-show"
    TVMAZE_SEASON = "tvmaze-season"
    TVMAZE_EPISODE = "tvmaze-episode"
    TVMAZE_PERSON = "tvmaze-person"
    TVMAZE_CHARACTER = "tvmaze-character"
    WIKIDATA = "wikidata"
    MUSICBRAINZ_ARTIST = "mb-artist"
    MUSICBRAINZ_RELEASE = "mb-release"
    MUSICBRAINZ_GROUP = "mb-group"
    MUSICBRAINZ_RECORDING = "mb-recording"
    MUSICBRAINZ_WORK = "mb-work"


OPEN_LIBRARY_IDS = {
    Namespace.OPEN_LIBRARY_WORK: ("/works/", "W"),
    Namespace.OPEN_LIBRARY_EDITION: ("/books/", "M"),
    Namespace.OPEN_LIBRARY_AUTHOR: ("/authors/", "A"),
}
NUMERIC_IDS = {
    namespace for namespace in Namespace if namespace.startswith(("tmdb-", "tvmaze-"))
}


def _isbn13(value):
    digits = re.sub(r"[-\s]", "", value.upper())
    if re.fullmatch(r"[0-9]{9}[0-9X]", digits):
        isbn10 = [int(digit) for digit in digits[:9]] + [
            10 if digits[-1] == "X" else int(digits[-1])
        ]
        if (
            sum(weight * digit for weight, digit in zip(range(10, 0, -1), isbn10)) % 11
            == 0
        ):
            base = "978" + digits[:9]
            checksum = (
                -sum(
                    int(digit) * (1 if i % 2 == 0 else 3)
                    for i, digit in enumerate(base)
                )
            ) % 10
            return base + str(checksum)
    if re.fullmatch(r"97[89][0-9]{10}", digits):
        if (
            sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(digits))
            % 10
            == 0
        ):
            return digits
    raise ValidationError("Enter a valid ISBN.")


def normalize_identifier(namespace, value):
    value = str(value).strip()
    if namespace == Namespace.ISBN:
        return _isbn13(value)
    if namespace in OPEN_LIBRARY_IDS:
        prefix, suffix = OPEN_LIBRARY_IDS[namespace]
        key = value.lower().removeprefix(prefix).upper()
        if re.fullmatch(rf"OL[1-9][0-9]{{0,15}}{suffix}", key):
            return key
    elif namespace in NUMERIC_IDS:
        if re.fullmatch(r"[0-9]{1,12}", value) and int(value):
            return str(int(value))
    elif namespace == Namespace.WIKIDATA:
        key = value.upper()
        if re.fullmatch(r"Q[1-9][0-9]{0,15}", key):
            return key
    elif namespace in Namespace and str(namespace).startswith("mb-"):
        try:
            return str(uuid.UUID(value))
        except ValueError:
            pass
    raise ValidationError("Identifier does not match its namespace.")
