from django.conf.urls import url
from rest_framework import routers

from ticket import viewsets

router = routers.DefaultRouter()
router.register(r'ticket/tickets', viewsets.TicketViewSet, base_name="ticket", )
router.register(r'ticket/lots', viewsets.LotViewSet, base_name="lot")

single_endpoints = [
    url(r'^ticket/event/(?P<event_pk>[\d]+)/calculator/(?P<price>\d+\.\d+)',
        viewsets.TicketCalculatorAPIView.as_view(),
        name='ticket-calculator'),
    url(r'^ticket/tickets/(?P<pk>[\d]+)/lots/current/',
        viewsets.TicketCurrentLotView.as_view(),
        name='ticket-lot-current'),
]

urlpatterns = router.urls
urlpatterns += single_endpoints
