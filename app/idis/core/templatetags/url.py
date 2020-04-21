from django import template
from django.urls.base import reverse

register = template.Library()


@register.simple_tag()
def url(view_name, *args, **kwargs):
    return reverse(view_name, args=args, kwargs=kwargs)
