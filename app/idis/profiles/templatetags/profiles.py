from typing import Union

from django import template
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def user_profile_link(user: Union[AbstractUser, None]) -> str:
    if user:
        username = user.username
        profile_url = reverse(
            "userena_profile_detail", kwargs={"username": user.username}
        )
        mugshot = format_html(
            (
                '<img class="mugshot" src="{0}" alt="User Mugshot"'
                # Match the "fa-lg" class style:
                '     style="height: 1.33em; vertical-align: -25%;"/>'
            ),
            user.user_profile.get_mugshot_url(),
        )
    else:
        username = "Unknown"
        profile_url = "#"
        mugshot = mark_safe('<i class="fas fa-user fa-lg"></i>')

    return format_html(
        '<a href="{0}">{1}</a>&nbsp;<a href="{0}">{2}</a>',
        profile_url,
        mugshot,
        username,
    )


@register.filter
def user_profile_link_username(username: str) -> str:
    User = get_user_model()  # noqa: N806
    return user_profile_link(User.objects.get(username=username))
