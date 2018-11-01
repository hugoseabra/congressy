from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

from gatheros_event.views.mixins import EventViewMixin
from gatheros_subscription.models import (
    Subscription,
)
from gatheros_subscription.views import SubscriptionViewMixin


class SubscriptionCancelView(EventViewMixin,
                             SubscriptionViewMixin, generic.DetailView):
    template_name = 'subscription/delete.html'
    model = Subscription
    success_message = 'Inscrição cancelada com sucesso.'
    cancel_message = 'Tem certeza que deseja cancelar?'
    model_protected_message = 'A entidade não pode ser cancelada.'
    place_organization = None
    object = None

    def get_object(self, queryset=None):
        """ Resgata objeto principal da view. """
        if not self.object:
            self.object = super(SubscriptionCancelView, self).get_object(
                queryset)

        return self.object

    def pre_dispatch(self, request):
        self.object = self.get_object()
        super(SubscriptionCancelView, self).pre_dispatch(request)

    def get_permission_denied_url(self):
        url = self.get_success_url()
        return url.format(**model_to_dict(self.object)) if self.object else url

    def get_context_data(self, **kwargs):
        context = super(SubscriptionCancelView, self).get_context_data(
            **kwargs)
        context['organization'] = self.organization
        context['go_back_path'] = self.get_success_url()
        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'

        # noinspection PyProtectedMember
        verbose_name = self.object._meta.verbose_name
        context['title'] = 'Cancelar {}'.format(verbose_name)

        data = model_to_dict(self.get_object())
        cancel_message = self.get_cancel_message()
        context['cancel_message'] = cancel_message.format(**data)
        return context

    def get_cancel_message(self):
        """
        Recupera mensagem de remoção a ser perguntada ao usuário antes da
        remoção.
        """
        return self.cancel_message

    def post(self, request, *args, **kwargs):
        try:

            pk = kwargs.get('pk')
            self.object = Subscription.objects.get(pk=pk)
            self.object.status = self.object.CANCELED_STATUS
            self.object.save()

            messages.success(request, self.success_message)

        except Exception as e:
            messages.error(request, str(e))

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('subscription:subscription-list', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })
