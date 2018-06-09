from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from raffle import forms, models


class RaffleListView(generic.ListView):
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
        return cxt


class RaffleAddView(generic.CreateView):
    template_name = 'raffle/raffle/form.html'
    form_class = forms.RaffleForm
    event = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('raffle:raffle-list', kwargs={
            'event_pk': self.event.pk,
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


class RaffleEditView(generic.UpdateView):
    template_name = 'raffle/raffle/form.html'
    form_class = forms.RaffleForm
    model = forms.RaffleForm.Meta.model
    event = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().dispatch(request, *args, **kwargs)

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


class RaffleDeleteView(generic.DeleteView):
    template_name = 'raffle/raffle/delete.html'
    model = models.Raffle
    event = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().dispatch(request, *args, **kwargs)

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


class RafflePanelView(generic.DetailView):
    template_name = 'raffle/raffle/panel.html'
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
        cxt['subscriptions'] = self.get_subscriptions()
        return cxt

    def get_subscriptions(self):
        return self.event.subscriptions.filter(
            attended=True,
        )


class WinnerListView(generic.ListView):
    template_name = 'raffle/winner/list.html'
    model = models.Winner
    event = None
    raffle = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        pk = self.kwargs.get('pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        self.raffle = get_object_or_404(models.Raffle, pk=pk)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(raffle=self.raffle)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt


class WinnerFormView(generic.FormView):
    template_name = 'raffle/winner/form.html'
    form_class = forms.WinnerForm
    event = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().dispatch(request, *args, **kwargs)

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


class WinnerDeleteView(generic.DeleteView):
    template_name = 'raffle/winner/delete.html'
    model = models.Winner
    event = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(event=self.event)

    def get_success_url(self):
        return reverse('raffle:winner-list', kwargs={
            'event_pk': self.event.pk,
        })

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['event'] = self.event
        return cxt
