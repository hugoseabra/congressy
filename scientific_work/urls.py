from django.conf.urls import include, url
from . import views

urls = [
    url(
        r'^add/$',
        views.WorkAddFormView.as_view(),
        name='work-add'
    ),
]

urlpatterns = [
    url(r'^subscription/(?P<subscription_pk>[0-9A-Fa-f-]+)/scientific_work/',
        include(urls))
]
