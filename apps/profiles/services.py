from django.db import transaction

from apps.core.policies import access_filter, viewer_owns

from .models import PageKey, Profile, ProfilePage


@transaction.atomic
def create_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        ProfilePage.objects.bulk_create(
            ProfilePage(profile=profile, key=key, position=position)
            for position, key in enumerate(PageKey.values)
        )
    return profile


def visible_profiles(viewer):
    return Profile.objects.select_related("user").filter(
        access_filter(viewer, owner_field="user_id"),
        user__is_active=True,
        user__email_verified=True,
    )


def visible_pages(profile, viewer, *, include_disabled_for_owner=False):
    pages = profile.pages.filter(
        access_filter(viewer, owner_field="profile__user_id"),
        profile__in=visible_profiles(viewer),
    )
    if include_disabled_for_owner and viewer_owns(viewer, profile.user_id):
        return pages
    return pages.filter(enabled=True)


@transaction.atomic
def update_page(owner, key, *, enabled, visibility):
    profile = Profile.objects.select_for_update().get(user=owner)
    return (
        profile.pages.filter(key=key).update(enabled=enabled, visibility=visibility)
        == 1
    )


@transaction.atomic
def move_page(owner, key, direction):
    profile = Profile.objects.select_for_update().get(user=owner)
    pages = list(profile.pages.all())
    for index, page in enumerate(pages):
        if page.key == key:
            break
    else:
        return False
    neighbour = index + direction
    if 0 <= neighbour < len(pages):
        other = pages[neighbour]
        page.position, other.position = other.position, page.position
        ProfilePage.objects.bulk_update([page, other], ["position"])
    return True
