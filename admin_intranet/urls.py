from django.conf.urls import url

from admin_intranet import views

urlpatterns = [
    url(
        r'^$',
        views.IndexView.as_view(),
        name='start'
    ),
]
