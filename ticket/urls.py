from django.conf.urls import url
from rest_framework import routers

from ticket import viewsets

router = routers.DefaultRouter()
router.register(r'ticket/tickets', viewsets.TicketViewSet, base_name="ticket", )
router.register(r'ticket/lots', viewsets.LotViewSet, base_name="lot")

single_endpoints = [
    url(r'^ticket/lots/(?P<event_pk>[\d]+)/calculator/(?P<price>\d+\.\d{2})',
        viewsets.TicketCalculatorAPIView.as_view(),
        name='ticket-calculator')
]

urlpatterns = router.urls
urlpatterns += single_endpoints
