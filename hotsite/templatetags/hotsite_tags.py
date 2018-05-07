from django import template

register = template.Library()


@register.simple_tag
def cat_get_lots(lot_category):
    return lot_category.lots.filter(active=True)


@register.simple_tag
def cat_has_active_lots(lot_category):
    return cat_get_lots(lot_category).count() > 0
