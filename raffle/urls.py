from django.conf.urls import include, url

from raffle import views


private_raffle_urls = [
    url(
        r'^raffles/winners/delete/$',
        views.WinnerDeleteView.as_view(),
        name='winner-delete'
    ),
    url(
        r'^raffles/(?P<pk>[\d]+)/winners/add/$',
        views.WinnerFormView.as_view(),
        name='winner-register'
    ),
    url(
        r'^raffles/(?P<pk>[\d]+)/winners/$',
        views.WinnerListView.as_view(),
        name='winner-list'
    ),
    url(
        r'^raffles/(?P<pk>[\d]+)/winners/$',
        views.WinnerListView.as_view(),
        name='winner-list'
    ),
    url(
        r'^raffle/(?P<pk>[\d]+)/delete/$',
        views.WinnerDeleteView.as_view(),
        name='raffle-delete'
    ),
    url(
        r'^raffles/(?P<pk>[\d]+)/edit/$',
        views.RaffleEditView.as_view(),
        name='raffle-edit'
    ),
    url(
        r'^raffles/(?P<pk>[\d]+)/$',
        views.RafflePanelView.as_view(),
        name='raffle-panel'
    ),
    url(
        r'^raffles/add/$',
        views.RaffleAddView.as_view(),
        name='raffle-add'
    ),
    url(
        r'^raffles/$',
        views.RaffleListView.as_view(),
        name='raffle-list'
    ),
]
urlpatterns_private_raffles = [
    url(r'^events/(?P<event_pk>[\d]+)/', include(private_raffle_urls))
]
