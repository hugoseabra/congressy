from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    url(
        r'^subscriptions/$',
        views.MySubscriptionsListView.as_view(),
        name='my-subscriptions'
    ),
]

urlpatterns_me = [url(r'^me/', include(urls))]
