from rest_framework import routers

from ticket import viewsets

router = routers.DefaultRouter()
router.register(r'tickets', viewsets.TicketViewSet)
router.register(r'lots', viewsets.LotViewSet)

urlpatterns = router.urls
