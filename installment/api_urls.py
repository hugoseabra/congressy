from rest_framework import routers
from installment import viewsets

router = routers.DefaultRouter()

router.register(
    r'installment/contracts',
    viewsets.InstallmentContractViewSet,
    base_name="installment_contract",
)

urlpatterns = router.urls

