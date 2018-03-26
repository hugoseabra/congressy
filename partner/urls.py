from django.conf.urls import include, url

from partner import views

public_partner_urls = [
    url(
        r'^$',
        views.RegistrationView.as_view(),
        name='partner-registration'
    ),
    url(
        r'^done/$',
        views.RegistrationDoneView.as_view(),
        name='partner-registration-done'
    ),
]

urlpatterns_public_partner = [url(r'^', include(public_partner_urls))]
