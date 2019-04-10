from rest_framework import routers

from ticket import viewsets

router = routers.DefaultRouter()
router.register(r'ticket/tickets', viewsets.TicketViewSet, base_name="ticket", )
router.register(r'ticket/lots', viewsets.LotViewSet, base_name="lot")

urlpatterns = router.urls
