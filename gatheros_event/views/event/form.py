from django import forms
from django.contrib import messages
from django.db.models.fields import BooleanField
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import six
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventAddFormView(AccountMixin, generic.CreateView):
    model = Event
    template_name = 'gatheros_event/event/form.html'
    fields = [
        'category',
        'name',
        'date_start',
        'date_end',
        'description',
        'subscription_type',
        'subscription_offline',
        'published'
    ]

    def get_context_data(self, **kwargs):
        context = super(EventAddFormView, self).get_context_data(**kwargs)
        context['form_title'] = 'Adicionar evento'

        return context

    def get(self, request, *args, **kwargs):
        if self.cannot_add():
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventAddFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.cannot_add():
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventAddFormView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, 'Evento criado com sucesso.')
        return super(EventAddFormView, self).form_valid(form)

    def get_success_url(self):
        form = self.get_form()
        event = form.instance
        return reverse(
            'gatheros_event:event-panel',
            kwargs={'pk': event.pk}
        )

    def cannot_add(self):
        can_add = self.request.user.has_perm(
            'gatheros_event.can_add_event',
            self.organization
        )
        if not can_add:
            messages.warning(
                self.request,
                "Você não tem permissão para adicionar evento"
            )

        return can_add is False


class EventEditFormView(AccountMixin, generic.UpdateView):
    model = Event
    template_name = 'gatheros_event/event/form.html'
    success_url = reverse_lazy('gatheros_event:event-list')
    fields = [
        'category',
        'name',
        'date_start',
        'date_end',
        'description',
        'subscription_type',
        'subscription_offline',
        'published'
    ]

    def get(self, request, *args, **kwargs):
        response = super(EventEditFormView, self).get(request, *args, **kwargs)
        if self.cannot_edit():
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return response

    def post(self, request, *args, **kwargs):
        if self.cannot_edit():
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventEditFormView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventEditFormView, self).get_context_data(**kwargs)
        context['title'] = '{} ({})'.format(self.object.name, self.object.pk)
        context['form_title'] = 'Editar evento #ID:' + str(self.object.pk)
        context['next_path'] = self._get_referer_url()

        return context

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, 'Evento alterado com sucesso.')
        return super(EventEditFormView, self).form_valid(form)

    def get_success_url(self):
        form_kwargs = self.get_form_kwargs()
        data = form_kwargs.get('data', {})
        next_path = data.get('next')
        if next_path:
            return next_path

        return super(EventEditFormView, self).get_success_url()

    def _get_referer_url(self):
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
            previous_url = previous_url.replace(host, '')

            if previous_url != request.path:
                return previous_url

        return self.success_url

    def cannot_edit(self):
        event = self.get_object()
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            event
        )
        if not can_edit:
            messages.warning(
                self.request,
                "Você não tem permissão para editar este evento"
            )

        return can_edit is False


class EventPatchFormView(AccountMixin, generic.View):
    http_method_names = ['post']
    model = Event
    object = None

    def post(self, request, **kwargs):
        def error_redirect():
            messages.warning(self.request, "Nenhum evento foi informado.")
            return redirect(reverse_lazy('gatheros_event:event-list'))

        pk = kwargs.get('pk')
        if not pk:
            return error_redirect()

        try:
            self.object = Event.objects.get(pk=pk)

        except Event.DoesNotExist:
            return error_redirect()

        else:
            if self.cannot_edit(request):
                return error_redirect()

            updated_field = []
            for key, value in six.iteritems(self.request.POST):
                if not hasattr(self.object, key):
                    continue

                field = self.object._meta.get_field(key)
                if isinstance(field, BooleanField):
                    value = value == 'true' or value == '1'

                setattr(self.object, key, value)
                updated_field.append(key)

            self.object.save(update_fields=updated_field)

        path = reverse('gatheros_event:event-panel', kwargs={'pk': pk})
        return redirect(path)

    def cannot_edit(self, request):
        can_edit = request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )
        if not can_edit:
            messages.warning(
                request,
                "Você não tem permissão para editar este evento"
            )

        return can_edit is False


class EventEditDatesForm(forms.Form):
    date_start = forms.DateTimeField(label='Data inicial')
    date_end = forms.DateTimeField(label='Data final')
    instance = None

    def save(self):
        self.instance.date_start = self.cleaned_data.get('date_start')
        self.instance.date_end = self.cleaned_data.get('date_end')
        self.instance.save()


class EventEditDatesFormView(AccountMixin, generic.FormView):
    form_class = EventEditDatesForm
    template_name = 'gatheros_event/event/form.html'
    object = None

    def error_redirect(self):
        messages.warning(self.request, "Nenhum evento foi informado.")
        return redirect(reverse_lazy('gatheros_event:event-list'))

    def get_initial(self):
        initial = super(EventEditDatesFormView, self).get_initial()
        initial['pk'] = self.object.pk
        initial['date_start'] = self.object.date_start
        initial['date_end'] = self.object.date_end

        return initial

    def get(self, request, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return self.error_redirect()

        try:
            self.object = Event.objects.get(pk=pk)

        except Event.DoesNotExist:
            return self.error_redirect()

        else:
            if self.cannot_edit(request):
                return self.error_redirect()

        return super(EventEditDatesFormView, self).get(request, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        try:
            self.object = Event.objects.get(pk=pk)

        except Event.DoesNotExist:
            return self.error_redirect()

        else:
            if self.cannot_edit(request):
                return self.error_redirect()

            return super(EventEditDatesFormView, self).post(
                request,
                *args,
                **kwargs
            )

    def form_valid(self, form):
        form.instance = self.object
        form.instance.organization = self.organization
        form.save()

        messages.success(self.request, 'Evento alterado com sucesso.')
        return super(EventEditDatesFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EventEditDatesFormView, self).get_context_data(
            **kwargs)
        context['title'] = '{} ({})'.format(self.object.name, self.object.pk)
        context['form_title'] = 'Alterar datas'
        context['next_path'] = self.get_success_url()

        return context

    def get_success_url(self):
        pk = self.object.pk
        return reverse('gatheros_event:event-panel', kwargs={'pk': pk})

    def cannot_edit(self, request):
        can_edit = request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )
        if not can_edit:
            messages.warning(
                request,
                "Você não tem permissão para editar este evento"
            )

        return can_edit is False
