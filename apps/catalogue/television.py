from django.core.paginator import Paginator

from .models import ItemKind, TVEpisode, TVSeason, TVShow
from .services import public_items


def television_context(item, page):
    eligible = public_items()
    if item.kind == ItemKind.SHOW:
        show = TVShow.objects.filter(item=item).first()
        if show:
            seasons = (
                show.seasons.filter(item__in=eligible)
                .select_related("item")
                .order_by("number")
            )
            characters = eligible.filter(tvshowcharacter__show=show).order_by(
                "title_key", "pk"
            )[:24]
            return {
                "show": show,
                "reference_page": Paginator(seasons, 24).get_page(page),
                "characters": characters,
            }
    elif item.kind == ItemKind.SEASON:
        season = (
            TVSeason.objects.select_related("show__item")
            .filter(item=item, show__item__in=eligible)
            .first()
        )
        if season:
            episodes = (
                season.episodes.filter(item__in=eligible)
                .select_related("item")
                .order_by("number", "pk")
            )
            return {
                "season": season,
                "reference_page": Paginator(episodes, 24).get_page(page),
            }
    elif item.kind == ItemKind.EPISODE:
        episode = (
            TVEpisode.objects.select_related("season__item", "season__show__item")
            .filter(
                item=item, season__item__in=eligible, season__show__item__in=eligible
            )
            .first()
        )
        if episode:
            return {"episode": episode}
    return {}
