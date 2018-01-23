from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^',
        views.FormConfigView.as_view(),
        name='form-config'
    ),
]

urlpatterns_formconfig = [
    url(r'^events/(?P<event_pk>[\d]+)/form-config/', include(urls)),
]
