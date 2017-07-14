from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event import forms
from gatheros_event.models import Event, Info
from gatheros_event.views.mixins import AccountMixin


class EventInfoView(AccountMixin, DetailView):
    model = Event
    template_name = 'gatheros_event/event/info.html'
    object = None
    show_reset_button = False

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self._can_view():
            return redirect(reverse_lazy('event:event-list'))

        return super(EventInfoView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventInfoView, self).get_context_data(**kwargs)
        config_type = self._get_selected_config_type()
        context['selected_config_type'] = config_type
        context['config_types'] = Info.CONFIG_TYPE_CHOICES
        context['show_reset_button'] = self.show_reset_button
        context['form'] = self._get_form(config_type)
        return context

    def _get_selected_config_type(self):
        config_type = self.request.GET.get('type')
        if config_type:
            self.show_reset_button = True
            return config_type

        try:
            info = self.object.info
            config_type = info.config_type
            if not config_type:
                config_type = Info.CONFIG_TYPE_MAIN_IMAGE

        except Info.DoesNotExist:
            config_type = Info.CONFIG_TYPE_MAIN_IMAGE

        self.show_reset_button = False
        return config_type

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _get_form(self, config_type, data=None, files=None):
        """
        Recupera o formulário correto conforme config_type

        :param config_type: String
        :param data: QueryDict - Dados do formulário
        :return: Formulário
        """

        if config_type == Info.CONFIG_TYPE_TEXT_ONLY:
            form_class = forms.InfoTextForm
        elif config_type == Info.CONFIG_TYPE_4_IMAGES:
            form_class = forms.Info4ImagesForm
        elif config_type == Info.CONFIG_TYPE_MAIN_IMAGE:
            form_class = forms.InfoMainImageForm
        elif config_type == Info.CONFIG_TYPE_VIDEO:
            form_class = forms.InfoVideoForm
        else:
            raise ImproperlyConfigured('Formulário não encontrado.')

        def new_form_instance(form_klass, instance=None):
            form_kwargs = {}

            if instance:
                form_kwargs.update({'instance': instance})

            if data:
                form_kwargs.update({'data': data})

            if files:
                form_kwargs.update({'files': files})

            return form_klass(**form_kwargs)

        try:
            info = self.object.info
            form = new_form_instance(form_class, instance=info)

        except Info.DoesNotExist:
            form = new_form_instance(form_class)

        form.initial.update({
            'config_type': config_type,
            'event': self.object.pk,
        })

        return form

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        data = request.POST
        form = self._get_form(
            config_type=data.get('config_type'),
            data=request.POST,
            files=request.FILES
        )

        form.files = request.FILES
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Informações de capa atualizadas com sucesso."
            )
        else:
            messages.error(request, "Informações de capa não atualizadas.")
            messages.error(request, form.errors)
            messages.error(request, form.non_field_errors())

        return redirect(reverse('event:event-info', kwargs={
            'pk': self.object.pk
        }))

    def _can_view(self):
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )
        same_organization = self.object.organization == self.organization
        return can_edit and same_organization
