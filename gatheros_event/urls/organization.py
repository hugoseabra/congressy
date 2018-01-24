""" Urls de `Organization` """
from django.conf.urls import include, url

from gatheros_event import views

urls = [
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.OrganizationDeleteView.as_view(),
        name='organization-delete'
    ),
    url(
        r'^(?P<pk>[\d]+)/cancel-membership/$',
        views.OrganizationCancelMembershipView.as_view(),
        name='organization-cancel-membership'
    ),
    url(
        r'^(?P<pk>[\d]+)/edit/$',
        views.OrganizationEditFormView.as_view(),
        name='organization-edit'
    ),
    url(
        r'^(?P<pk>[\d]+)/financial/edit/$',
        views.OrganizationFinancialEditFormView.as_view(),
        name='organization-financial-edit'
    ),
    url(
        r'^add/$',
        views.OrganizationAddFormView.as_view(),
        name='organization-add'
    ),
    url(
        r'^add-internal/$',
        views.OrganizationAddInternalFormView.as_view(),
        name='organization-add-internal'
    ),
    url(
        r'^(?P<pk>[\d]+)/$',
        views.OrganizationPanelView.as_view(),
        name='organization-panel'
    ),
    url(
        r'^switch/$',
        views.OrganizationSwitch.as_view(),
        name='organization-switch'
    ),
    url(
        r'^$',
        views.OrganizationListView.as_view(),
        name='organization-list'
    ),
]

urlpatterns_organization = [url(r'^organizations/', include(urls))]
