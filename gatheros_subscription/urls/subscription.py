from django.conf.urls import include, url

from gatheros_subscription import views

urls = [
    # url(
    #     r'^(?P<pk>[0-9A-Fa-f-]+)/delete/$',
    #     views.SubscriptionCancelView.as_view(),
    #     name='subscription-delete'
    # ),
    url(
        r'^add/$',
        views.SubscriptionAddFormView.as_view(),
        name='subscription-add'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/check-in$',
        views.SubscriptionUpdateAttendedAPIView.as_view(),
        name='subscription-api-update-check-in'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/attendance/$',
        views.SubscriptionAttendanceView.as_view(),
        name='subscription-attendance'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/edit/$',
        views.SubscriptionEditFormView.as_view(),
        name='subscription-edit'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/payments/delete/$',
        views.PaymentDeleteView.as_view(),
        name='payment-delete'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/payments/$',
        views.SubscriptionViewFormView.as_view(financial=True),
        name='subscription-payments'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/switch-test/$',
        views.SwitchSubscriptionTestView.as_view(),
        name='subscription-switch-test'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/voucher/$',
        views.VoucherSubscriptionPDFView.as_view(),
        name='subscription-voucher'
    ),
    url(
        r'^(?P<pk>[0-9A-Fa-f-]+)/',
        views.SubscriptionViewFormView.as_view(),
        name='subscription-view'
    ),

    url(
        r'^attendance/dashboard/$',
        views.SubscriptionAttendanceDashboardView.as_view(),
        name='subscription-attendance-dashboard'
    ),
    url(
        r'^attendance/search/$',
        views.SubscriptionAttendanceSearchView.as_view(),
        name='subscription-attendance-search'
    ),
    url(
        r'^attendance/list/$',
        views.SubscriptionAttendanceListView.as_view(),
        name='subscription-attendance-list'
    ),
    url(
        r'^api/attendance/search/$',
        views.SubscriptionSearchViewSet.as_view(),
        name='subscription-api-attendance-search'
    ),
    url(
        r'^export/$',
        views.SubscriptionExportView.as_view(),
        name='subscriptions-export'
    ),
    url(
        r'^import/csv/(?P<csv_pk>[0-9A-Fa-f-]+)/prepare$',
        views.CSVPrepareView.as_view(),
        name='subscriptions-csv-file-prepare'
    ),
    url(
        r'^import/csv/(?P<csv_pk>[0-9A-Fa-f-]+)/process$',
        views.CSVProcessView.as_view(),
        name='subscriptions-csv-file-process'
    ),
    url(
        r'^import/csv/upload$',
        views.CSVFileImportView.as_view(),
        name='subscriptions-csv-file-import'
    ),
    url(
        r'^import/csv/$',
        views.CSVListView.as_view(),
        name='subscriptions-csv-list'
    ),
    url(
        r'^$',
        views.SubscriptionListView.as_view(),
        name='subscription-list'
    ),
]

urlpatterns_subscription = [
    url(r'^events/(?P<event_pk>[\d]+)/subscriptions/', include(urls)),
]
