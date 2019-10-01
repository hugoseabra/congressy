# pylint: skip-file

from rest_framework import routers

from payment import viewsets

router = routers.DefaultRouter()

# router.register(r'payer/payers',
#                 viewsets.Pay,
#                 base_name='payer')
# router.register(r'payer/benefactors',
#                 viewsets.ProductViewSet,
#                 base_name='benefactor')

urlpatterns = router.urls
