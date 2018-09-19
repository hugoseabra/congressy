from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from gatheros_event.models import Event
from gatheros_event.views.mixins import EventDraftStateMixin, AccountMixin
from raffle import forms, models


class RaffleBaseMixin(ContextMixin, AccountMixin, EventDraftStateMixin):
    permission_denied_message = 'Você não pode realizar esta ação.'

    def __init__(self, *args, **kwargs):
        self.event = None
        super().__init__(*args, **kwargs)

    def pre_dispatch(self, request):
        response = super().pre_dispatch(request)
        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk'),
        )

        features = self.event.feature_configuration

        if not features.feature_raffle:
            raise PermissionDenied(self.get_permission_denied_message())

        return response

    def get_permission_denied_url(self):
        return reverse(
            'event:event-panel',
            kwargs={
                'pk': self.event.pk,
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_event_state_context_data(self.event))
        return context


class RaffleListView(RaffleBaseMixin, generic.ListView):
    template_name = 'raffle/raffle/list.html'
    model = models.Raffle
    event = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        cxt['has_inside_bar'] = True
        cxt['active'] = 'raffles'
        return cxt


class RaffleAddView(generic.CreateView, RaffleBaseMixin):
    template_name = 'raffle/raffle/form.html'
    form_class = forms.RaffleForm

    def get_success_url(self):
        return reverse('raffle:raffle-panel', kwargs={
            'event_pk': self.event.pk,
            'pk': self.object.pk,
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt


class RaffleEditView(generic.UpdateView, RaffleBaseMixin):
    template_name = 'raffle/raffle/form.html'
    form_class = forms.RaffleForm
    model = forms.RaffleForm.Meta.model

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt

    def get_success_url(self):
        return reverse('raffle:raffle-list', kwargs={
            'event_pk': self.event.pk,
        })


class RaffleDeleteView(generic.DeleteView, RaffleBaseMixin):
    template_name = 'raffle/raffle/delete.html'
    model = models.Raffle

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_success_url(self):
        return reverse('raffle:raffle-list', kwargs={
            'event_pk': self.event.pk,
        })

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt


class RafflePanelView(generic.DetailView, RaffleBaseMixin):
    template_name = 'raffle/raffle/panel.html'
    model = models.Raffle

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        cxt['subscriptions'] = self.get_subscriptions()
        return cxt

    def get_subscriptions(self):
        queryset = self.event.subscriptions.filter(
            completed=True,
            test_subscription=False,
        )
        if self.object.attended_only is True:
            queryset = queryset.filter(attended=True)

        return queryset


class WinnerListView(generic.ListView, RaffleBaseMixin):
    template_name = 'raffle/winner/list.html'
    model = models.Winner
    event = None
    raffle = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        pk = self.kwargs.get('pk')
        self.raffle = get_object_or_404(models.Raffle, pk=pk)
        return response

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(raffle=self.raffle)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt


class WinnerFormView(generic.FormView, RaffleBaseMixin):
    template_name = 'raffle/winner/form.html'
    form_class = forms.WinnerForm
    object = None

    def get_success_url(self):
        return reverse('raffle:winner-register', kwargs={
            'event_pk': self.event.pk,
            'pk': self.kwargs.get('pk'),
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        cxt['object'] = self.object
        return cxt

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        data['raffle'] = self.kwargs.get('pk')
        request.POST = data
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class WinnerDeleteView(generic.DeleteView, RaffleBaseMixin):
    model = models.Winner
    http_method_names = ['post']
    object_pk = None

    def delete(self, request, *args, **kwargs):
        self.object_pk = request.POST.get('pk')
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse('')

    def get_object(self, queryset=None):
        return get_object_or_404(models.Winner, pk=self.object_pk)

    def get_success_url(self):
        return reverse('raffle:winner-list', kwargs={
            'event_pk': self.event.pk,
        })

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt
