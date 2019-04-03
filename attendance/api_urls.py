# pylint: skip-file
from django.conf.urls import url
from rest_framework import routers

from attendance import viewsets

router = routers.DefaultRouter()

router.register(
    r'attendance/services',
    viewsets.AttendanceServiceViewSet
)
router.register(
    r'attendance/services/(?P<service_pk>[\d]+)/subscriptions',
    viewsets.SubscriptionAttendanceViewSet,
)

router.register(r'attendance/checkins', viewsets.CheckinViewSet)
router.register(r'attendance/checkouts', viewsets.CheckoutViewSet)
single_endpoints = [
    url(r'^attendance/services/(?P<service_pk>[\d]+)/export/',
        viewsets.AttendanceServiceExporterViewSet.as_view())
]

urlpatterns = single_endpoints
urlpatterns += router.urls
