from django.conf.urls import url, include

from importer import views

urls = [
    url(
        r'^csv/(?P<csv_pk>[0-9A-Fa-f-]+)/prepare$',
        views.CSVPrepareView.as_view(),
        name='csv-file-prepare'
    ),
    url(
        r'^csv/(?P<csv_pk>[0-9A-Fa-f-]+)/process$',
        views.CSVProcessView.as_view(),
        name='csv-file-process'
    ),
    url(
        r'^csv/(?P<csv_pk>[0-9A-Fa-f-]+)/delete',
        views.CSVDeleteView.as_view(),
        name='csv-file-delete'
    ),
    url(
        r'^csv/(?P<csv_pk>[0-9A-Fa-f-]+)/error_file/xls',
        views.CSVErrorXLSView.as_view(),
        name='csv-file-error-xls'
    ),
    url(
        r'^csv/upload$',
        views.CSVFileImportView.as_view(),
        name='csv-file-import'
    ),
    url(
        r'^csv/$',
        views.CSVListView.as_view(),
        name='csv-list'
    ),
]

urlpatterns = [
    url(r'^events/(?P<event_pk>[\d]+)/subscriptions/import/', include(urls)),
]
