from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from gatheros_event.models import Event
from gatheros_subscription.forms import (
    SubscriptionFilterForm,
)
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.models import (
    Subscription,
)
from gatheros_subscription.views import SubscriptionViewMixin


class SubscriptionExportView(SubscriptionViewMixin, generic.View):
    http_method_names = ['post']
    template_name = 'subscription/export.html'
    form_class = SubscriptionFilterForm
    model = Subscription
    paginate_by = 5
    allow_empty = True
    event = None

    def get_event(self):
        if self.event:
            return self.event

        self.event = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        return self.event

    def post(self, request, *args, **kwargs):
        # Chamando exportação
        output = export_event_data(self.get_event())

        # Criando resposta http com arquivo de download
        response = HttpResponse(
            output,
            content_type="application/vnd.ms-excel"
        )

        # Definindo nome do arquivo
        event = self.get_event()
        name = "%s_%s.xlsx" % (
            event.slug,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % name

        return response

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            Event.objects.get(pk=self.kwargs.get('event_pk'))
        )
