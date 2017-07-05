from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event import forms
from gatheros_event.views.mixins import AccountMixin


def update_banners(request, event):
    form = forms.EventBannerForm(
        instance=event,
        data=request.POST,
        files=request.FILES
    )
    if form.is_valid():
        form.save()
        messages.success(request, "Banners atualizados com sucesso.")
    else:
        messages.error(request, "Dados não atualizados.")
        messages.error(request, form.errors)
        messages.error(request, form.non_field_errors())

    return redirect(reverse('gatheros_event:event-detail', kwargs={
        'pk': event.pk
    }))


def update_place(request, event):
    form = forms.EventPlaceForm(instance=event, data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Local atualizado com sucesso.")
    else:
        messages.error(request, "Dados não atualizados.")
        messages.error(request, form.errors)
        messages.error(request, form.non_field_errors())

    return redirect(reverse('gatheros_event:event-detail', kwargs={
        'pk': event.pk
    }))


def update_social_media(request, event):
    form = forms.EventSocialMediaForm(instance=event, data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(
            request,
            "Informações sociais atualizadas com sucesso."
        )
    else:
        messages.error(request, "Dados não atualizados.")
        messages.error(request, form.errors)
        messages.error(request, form.non_field_errors())

    return redirect(reverse('gatheros_event:event-detail', kwargs={
        'pk': event.pk
    }))


class EventDetailView(AccountMixin, DetailView):
    model = forms.EventBannerForm.Meta.model
    template_name = 'gatheros_event/event/detail.html'
    object = None

    def get_object(self, queryset=None):
        if self.object:
            return self.object

        return super(EventDetailView, self).get_object(queryset)

    def pre_dispatch(self, request):
        self.object = self.get_object()

    def get_permission_denied_url(self):
        return reverse_lazy('gatheros_event:event-list')

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['banner_form'] = forms.EventBannerForm(instance=self.object)
        context['place_form'] = forms.EventPlaceForm(instance=self.object)
        context['socialmedia_form'] = forms.EventSocialMediaForm(
            instance=self.object
        )
        return context

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        submit_type = data.get('submit_type')
        supported_types = (
            'update_banners',
            'update_place',
            'update_social_media',
        )

        update_function = eval(submit_type)
        if not submit_type \
                or (submit_type not in supported_types) \
                and not callable(update_function):
            raise ImproperlyConfigured(
                'Formulário não configurado corretamente. Insira um campo'
                ' do tipo `hidden` com um dos seguintes tipos: ' +
                ', '.join(supported_types)
            )

        return update_function(request, self.object)

    def can_access(self):
        event = self.get_object()
        can_edit = self.request.user.has_perm(
            'gatheros_event.change_event',
            event
        )
        same_organization = event.organization.pk == self.organization.pk
        return can_edit and same_organization
