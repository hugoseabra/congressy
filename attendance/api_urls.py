# pylint: skip-file

from rest_framework import routers

from attendance import viewsets

router = routers.DefaultRouter()

router.register(
    r'attendance/services',
    viewsets.AttendanceServiceViewSet
)

router.register(r'attendance/checkins', viewsets.CheckinViewSet)
router.register(r'attendance/checkouts', viewsets.CheckoutViewSet)

urlpatterns = router.urls
