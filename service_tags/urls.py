from django.conf.urls import url

from . import views

service_tags_urlpatterns = [

    url(
        r'^remarketing/redirect/$',
        views.RemarketingRedirectLanding.as_view(),
        name='remarketing-redirect'
    ),
    
]
