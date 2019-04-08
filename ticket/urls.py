from rest_framework import routers

from ticket import viewsets

router = routers.DefaultRouter()
router.register(r'ticket/tickets', viewsets.TicketViewSet)
router.register(r'ticket/lots', viewsets.LotViewSet)

urlpatterns = router.urls
