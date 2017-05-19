from django import forms
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import BooleanField
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import View, generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


# @TODO Levar forms para raiz forms.py


class BaseEventView(AccountMixin, View):
    success_message = ''
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        if self.cannot_view():
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(BaseEventView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        # noinspection PyUnresolvedReferences
        return super(BaseEventView, self).form_valid(form)

    def _get_referer_url(self):
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
            previous_url = previous_url.replace(host, '')

            if previous_url != request.path:
                return previous_url

        return self.success_url

    def cannot_view(self):
        raise NotImplemented()


class BaseEventPatchFormView(BaseEventView):
    object = None

    def dispatch(self, request, *args, **kwargs):
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

        return super(BaseEventPatchFormView, self).dispatch(
            request,
            *args,
            **kwargs
        )


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'organization',
            'category',
            'name',
            'date_start',
            'date_end',
            'description',
            'subscription_type',
            'subscription_offline',
            'published'
        ]
        widgets = {'organization': forms.HiddenInput()}


class EventAddFormView(generic.CreateView, BaseEventView):
    form_class = EventForm
    template_name = 'gatheros_event/event/form.html'
    success_message = 'Evento criado com sucesso.'

    def get_initial(self):
        initial = super(EventAddFormView, self).get_initial()
        initial['organization'] = self.organization

        return initial

    def get_context_data(self, **kwargs):
        context = super(EventAddFormView, self).get_context_data(**kwargs)

        form_title = "Novo evento"
        if not self.organization.internal:
            form_title += " para '" + self.organization.name + "'"

        context['form_title'] = form_title

        return context

    def get_success_url(self):
        form = self.get_form()
        event = form.instance
        return reverse(
            'gatheros_event:event-panel',
            kwargs={'pk': event.pk}
        )

    def cannot_view(self):
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


class EventEditFormView(generic.UpdateView, BaseEventView):
    form_class = EventForm
    model = EventForm.Meta.model
    template_name = 'gatheros_event/event/form.html'
    success_url = reverse_lazy('gatheros_event:event-list')
    success_message = 'Evento alterado com sucesso.'

    def get_initial(self):
        initial = super(EventEditFormView, self).get_initial()
        initial['organization'] = self.organization

    def get_context_data(self, **kwargs):
        context = super(EventEditFormView, self).get_context_data(**kwargs)
        context['title'] = '{} ({})'.format(self.object.name, self.object.pk)
        context['form_title'] = 'Editar evento #ID:' + str(self.object.pk)
        context['next_path'] = self._get_referer_url()

        return context

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

    def cannot_view(self):
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


class EventPatchFormView(BaseEventPatchFormView):
    http_method_names = ['post']
    model = Event

    # noinspection PyUnusedLocal
    def post(self, request, **kwargs):
        updated_field = []
        for key, value in six.iteritems(self.request.POST):
            if not hasattr(self.object, key):
                continue

            # noinspection PyProtectedMember
            field = self.object._meta.get_field(key)
            if isinstance(field, BooleanField):
                value = value == 'true' or value == '1'

            setattr(self.object, key, value)
            updated_field.append(key)

        self.object.save(update_fields=updated_field)

        return redirect(reverse(
            'gatheros_event:event-panel',
            kwargs={'pk': self.object.pk}
        ))

    def cannot_view(self):
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )
        if not can_edit:
            messages.warning(
                self.request,
                "Você não tem permissão para editar este evento"
            )

        return can_edit is False


class BaseSimpleFormView(generic.FormView, BaseEventPatchFormView):
    template_name = None
    form_title = 'Alterar'
    object = None
    success_message = 'Evento alterado com sucesso.'

    def get_initial(self):
        initial = super(BaseSimpleFormView, self).get_initial()
        initial['pk'] = self.object.pk

        return initial

    def form_valid(self, form):
        form.instance = self.object
        form.instance.organization = self.organization
        form.save()

        return super(BaseSimpleFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BaseSimpleFormView, self).get_context_data(
            **kwargs)
        context['title'] = '{} ({})'.format(self.object.name, self.object.pk)
        context['form_title'] = self.form_title
        context['next_path'] = self.get_success_url()

        return context

    def get_success_url(self):
        pk = self.object.pk
        return reverse('gatheros_event:event-panel', kwargs={'pk': pk})

    def cannot_view(self):
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )
        if not can_edit:
            messages.warning(
                self.request,
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


class EventEditDatesFormView(BaseSimpleFormView):
    form_class = EventEditDatesForm
    template_name = 'gatheros_event/event/form.html'
    form_title = 'Alterar datas'

    def get_initial(self):
        initial = super(EventEditDatesFormView, self).get_initial()
        initial['date_start'] = self.object.date_start
        initial['date_end'] = self.object.date_end

        return initial


class EventEditSubscriptionTypeForm(forms.Form):
    subscription_type = forms.ChoiceField(
        label='Inscrições',
        widget=forms.Select
    )

    subscription_offline = forms.BooleanField(
        label='Inscrições offline',
        required=False
    )
    instance = None

    def __init__(self, *args, **kwargs):
        super(EventEditSubscriptionTypeForm, self).__init__(*args, **kwargs)
        self.fields['subscription_type'].choices = Event.SUBSCRIPTION_CHOICES

    def save(self):
        self.instance.subscription_type = \
            self.cleaned_data.get('subscription_type')
        self.instance.subscription_offline = \
            self.cleaned_data.get('subscription_offline')
        self.instance.save()


class EventEditSubscriptionTypeFormView(BaseSimpleFormView):
    form_class = EventEditSubscriptionTypeForm
    template_name = 'gatheros_event/event/form.html'
    form_title = 'Alterar tipo de inscrição'

    def get_initial(self):
        initial = super(EventEditSubscriptionTypeFormView, self).get_initial()
        initial['subscription_type'] = self.object.subscription_type
        initial['subscription_offline'] = self.object.subscription_offline

        return initial


class EventSimpleEditView(View):
    """View para formulários simples de event"""

    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Use this method within urls.py.
        We need to override this method because we can render different
        views from this to simplify urls setups.
        """
        return cls.get_view(**kwargs)

    @classmethod
    def get_view(cls, view_name=None, **kwargs):
        view_name = view_name or kwargs.pop(
            'view_name',
            getattr(cls, 'view_name', None)
        ) or None

        views = {
            'dates': EventEditDatesFormView,
            'subscription_type': EventEditSubscriptionTypeFormView
        }

        if view_name in views:
            view = views[view_name]
            return view.as_view(**kwargs)

        raise ImproperlyConfigured(
            'EventSimpleEditView() não está configurado corretamente em'
            ' urls.py. Configure utilizando'
            ' `EventSimpleEditView.as_view(view_name=\'<nome_da_view>\')`.'
            ' Os nomes de views possíveis são: ' + ', '.join(views.keys())
        )
