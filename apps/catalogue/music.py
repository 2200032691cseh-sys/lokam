from apps.integrations.adapters import MUSIC_ENDPOINTS
from apps.integrations.musicbrainz import listening_link

from .models import ItemKind, MusicRecording, MusicRelease
from .services import public_items


def music_context(item):
    if item.kind not in MUSIC_ENDPOINTS:
        return {}
    visible = public_items()
    links = [
        valid
        for entry in item.music_links.order_by("pk")[:12]
        if (valid := listening_link(entry.url))
    ]
    context = {"listening_links": links}
    if item.kind == ItemKind.MUSIC_ARTIST:
        context["artist"] = getattr(item, "music_artist", None)
    elif item.kind == ItemKind.MUSIC_ALBUM:
        context["album"] = getattr(item, "music_album", None)
        context["music_releases"] = (
            MusicRelease.objects.filter(album__item=item, item__in=visible)
            .select_related("item")
            .order_by("release_date", "pk")[:24]
        )
    elif item.kind == ItemKind.MUSIC_RELEASE:
        context["music_release"] = (
            MusicRelease.objects.select_related("album__item").filter(item=item).first()
        )
    elif item.kind == ItemKind.MUSIC_RECORDING:
        recording = (
            MusicRecording.objects.select_related("work__item")
            .filter(item=item)
            .first()
        )
        context["music_recording"] = recording
        if recording and recording.duration_ms is not None:
            minutes, seconds = divmod(recording.duration_ms // 1000, 60)
            context["music_duration"] = f"{minutes}:{seconds:02d}"
    elif item.kind == ItemKind.MUSICAL_WORK:
        context["work_recordings"] = (
            MusicRecording.objects.filter(work__item=item, item__in=visible)
            .select_related("item")
            .order_by("item__title_key", "pk")[:24]
        )
    return context
