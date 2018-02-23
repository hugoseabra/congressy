from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns_public = [
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    # url(r'^pdf/$', views.MyPDF.as_view(), name='pdf'),
]

urlpatterns_private = [
    url(r'^$', views.start, name='start'),
]

urlpatterns_public = [url(r'^', include(urlpatterns_public))]
urlpatterns_private = [url(r'^', include(urlpatterns_private))]
