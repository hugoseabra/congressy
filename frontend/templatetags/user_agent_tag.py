"""
gatheros_subscription templatetags
"""
from django import template

register = template.Library()


@register.filter(name='is_chrome')
def is_chrome(request):
    return 'chrome' in str(request.user_agent).lower()
