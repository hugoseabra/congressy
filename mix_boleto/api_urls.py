# pylint: skip-file

from django.conf.urls import url

from mix_boleto import viewsets

urlpatterns = [
    url(r'mix_boleto/sync/', viewsets.synchronization_hook, name='sync')
]
