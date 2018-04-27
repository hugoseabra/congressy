""" Urls dos opcionais """
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'category/(?P<category_pk>[\d]+)/products/',
        views.EventProductOptionalManagementView.as_view(),
        name='available_optional_product_list'),
]
