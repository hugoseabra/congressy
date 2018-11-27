from django.conf.urls import url
from rest_framework import routers

from installment import viewsets

router = routers.DefaultRouter()

router.register(
    r'installment/contracts',
    viewsets.ContractViewSet,
    base_name="installment_contract",
)

router.register(
    r'installment/parts',
    viewsets.PartViewSet,
    base_name="installment_part",
)

single_endpoints = [
    url(r'^installment/contracts/(?P<pk>[\d]+)/parts',
        viewsets.PartsList.as_view(),
        name='installment_contract-parts-list'),
]

urlpatterns = router.urls
urlpatterns += single_endpoints
