from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from gatheros_subscription.views import SubscriptionViewMixin
from importer.models import CSVFileConfig


class CSVViewMixin(SubscriptionViewMixin):
    """
        Mixin utilizado para não permitir acesso sem determinada flag ativada.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not self.event.feature_configuration.feature_import_via_csv:

            if request.is_ajax():
                message = 'Evento não permite importação via CSV'
                return JsonResponse({'error': message}, status=403)

            else:

                messages.error(request,
                               "Evento não permite importação via CSV.")

                url = reverse_lazy(
                    "subscription:subscription-list",
                    kwargs={
                        'event_pk': self.event.pk
                    }
                )

                return redirect(url)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'
        return context


class CSVProcessedViewMixin(CSVViewMixin, generic.DetailView):
    """
        Mixin utilizado para não permitir acesso caso
        arquivo já tenha sido processado.
    """

    object = None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.event = self.get_event()

        if self.object.processed:
            msg = "Arquivo já processado não pode ser processado novamente"
            messages.error(request, msg)
            return redirect(
                reverse_lazy('importer:csv-list', kwargs={
                    'event_pk': self.event.pk
                })
            )

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            CSVFileConfig,
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )
