from django.conf.urls import include, url

from gatheros_subscription import views

# prefix é 'event-' porque a relação é de 1-1 e fica mais simples de encontrar
# dados de 'Event' por causa das relações entre models.
url_fields = [
    url(
        r'^(?P<pk>[\d]+)/requirement/$',
        views.EventFormFieldManageRequirementView.as_view(),
        name='event-manage-requirement'
    ),
    url(
        r'^(?P<pk>[\d]+)/activation/$',
        views.EventFormFieldManageActivationView.as_view(),
        name='event-manage-activation'
    ),
    url(
        r'^(?P<pk>[\d]+)/order/$',
        views.EventFormFieldReorderView.as_view(),
        name='event-field-order'
    ),
    url(
        r'^(?P<pk>[\d]+)/delete/$',
        views.EventFormFieldRemoveView.as_view(),
        name='event-field-remove'
    ),
    url(
        r'^add/$',
        views.EventFormFieldAddView.as_view(),
        name='event-field-add'
    ),
    url(
        r'^',
        views.EventConfigFormFieldView.as_view(),
        name='event-fields-config'
    ),
]


urlpatterns_form = [
    url(r'^events/(?P<event_pk>[\d]+)/fields/', include(url_fields))
]
