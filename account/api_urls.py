# pylint: skip-file

from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'create',
                viewsets.AccountCreateViewset,
                base_name='account-create')

urlpatterns = router.urls
