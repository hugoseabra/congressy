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
    url(r'^events/(?P<event_pk>[\d]+)/scientific_work/', include(urls))
]
