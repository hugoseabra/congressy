"""
gatheros_subscription templatetags
"""
from django import template

from attendance.models import Checkin

register = template.Library()


@register.simple_tag
def count_checkins(service):
    return Checkin.objects.filter(
        attendance_service_id=service.pk,
        checkout__isnull=True,
    ).order_by('subscription_id').distinct('subscription_id').count()
