"""
service_tags templatetags
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def process_template(context, content):
    t = template.Template(content)
    return t.render(context)
