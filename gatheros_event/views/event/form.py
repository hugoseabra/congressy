from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from formtools.wizard.views import SessionWizardView

from core.view.user_context import UserContextViewMixin
from gatheros_event.models import Member
from .wizard_steps import \
    EventFormBasicData, \
    EventFormPlaceNew


# @TODO RESOLVER: Super usuário não consegue criar evento por causa do contexto

def add_new_place(wizard):
    form = wizard.get_form(step='step2')
    return form.add_new_place is True


class ManagerView(UserContextViewMixin, SessionWizardView):
    model_name = 'event'
    template_name = 'gatheros_event/event/wizard/wizard.html'

    form_list = [
        ('step1', EventFormBasicData),
        ('step2', EventFormPlaceNew),
    ]
    file_storage = FileSystemStorage(settings.MEDIA_ROOT)

    def get_context_data(self, form, **kwargs):
        context = super(ManagerView, self).get_context_data(form, **kwargs)
        context['organization'] = self.user_context.active_organization
        return context

    def get_template_names(self):
        form = self.get_form()
        if hasattr(form, 'template_name'):
            return form.template_name

        return self.template_name

    def done(self, form_list, **kwargs):
        instance = self._save_data(form_list)
        messages.success(self.request, 'Evento criado com sucesso.')
        return HttpResponseRedirect(reverse_lazy(
            'gatheros_event:event-panel',
            kwargs={'pk': instance.pk}
        ))

    def render_to_response(self, context, **response_kwargs):
        if not self.can_add():
            messages.warning(
                self.request,
                "Você não tem permissão para adicionar evento"
            )
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(ManagerView, self).render_to_response(
            context=context,
            **response_kwargs
        )

    def can_add(self):
        # @TODO Aplicar ACL
        if self.request.user.is_superuser:
            return True

        active_member = self.user_context.active_member_group
        return active_member.group == Member.ADMIN

    def _save_data(self, form_list):
        dict_data = self._group_data_by_model(form_list)

        model_to_return = None
        prev_instance = None
        for model, dict_value in dict_data:
            instance = model(**dict_value['data'])
            instance.save()

            class_name = instance.__class__.__name__.lower()
            if class_name == self.model_name:
                model_to_return = instance

            if prev_instance:
                if hasattr(prev_instance, class_name):
                    setattr(prev_instance, class_name, instance)
                    prev_instance.save()

            prev_instance = instance

        return model_to_return

    def _group_data_by_model(self, form_list):
        dict_data = {}

        for form in form_list:
            model = form.Meta.model
            if model not in dict_data:
                dict_data[model] = {
                    'prefix': form.prefix,
                    'data': {}
                }

            dict_data[model]['data'].update(form.cleaned_data)

        dict_data = sorted(
            dict_data.items(),
            key=lambda item: item[1].get('prefix')
        )

        return dict_data


class EventEditView(UserContextViewMixin, UpdateView):
    form_class = EventFormBasicData
    model = EventFormBasicData.Meta.model
    template_name = 'gatheros_event/event/form_edit.html'
    success_url = reverse_lazy('gatheros_event:event-list')

    def form_valid(self, form):
        response = super(EventEditView, self).form_valid(form)
        messages.success(self.request, 'Evento alterado com sucesso.')
        return response

    def render_to_response(self, context, **response_kwargs):
        if not self.can_edit():
            messages.warning(
                self.request,
                "Você não tem permissão para editar este evento"
            )
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventEditView, self).render_to_response(
            context=context,
            **response_kwargs
        )

    def can_edit(self):
        # @TODO Aplicar ACL
        if self.request.user.is_superuser:
            return True

        active_member = self.user_context.active_member_group
        return active_member.group in [
            Member.ADMIN,
            Member.HELPER,
        ]


class EventWizardView(ManagerView):
    pass
