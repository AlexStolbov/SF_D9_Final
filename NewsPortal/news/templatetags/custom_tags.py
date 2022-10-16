from datetime import datetime
from django import template

register = template.Library()


@register.simple_tag()
def current_time(format_string='%b %d %Y'):
    return datetime.utcnow().strftime(format_string)


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    params = context['request'].GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    return params.urlencode()
