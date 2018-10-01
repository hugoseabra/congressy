from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import DeleteViewMixin, \
    MultiLotsFeatureFlagMixin, EventDraftStateMixin, AccountMixin
from gatheros_subscription import forms
from gatheros_subscription.models import LotCategory

try:
    from raven.contrib.django.raven_compat.models import client

    SENTRY_RAVEN = True

except ImportError:
    SENTRY_RAVEN = False


class LotCategoryListView(AccountMixin, generic.ListView, EventDraftStateMixin):
    """Lista de lotes de acordo com o evento do contexto"""
    model = LotCategory
    template_name = 'lotcategory/list.html'
    ordering = ['name']
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        else:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['has_inside_bar'] = True
        context['active'] = 'categorias'
        context['is_paid_event'] = is_paid_event(self.event)

        context.update(self.get_event_state_context_data(self.event))

        return context

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        return LotCategory.objects.filter(event=self.event).order_by('pk')


class LotCategoryAddView(MultiLotsFeatureFlagMixin, generic.CreateView,
                         EventDraftStateMixin):
    form_class = forms.LotCategoryForm
    template_name = 'lotcategory/form.html'
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        else:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('subscription:category-list', kwargs={
            'event_pk': self.event.pk,
        })

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event

        context.update(self.get_event_state_context_data(self.event))

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'event': self.event})
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(self.request, 'Categoria de lote criada com sucesso.')
        return response


class LotCategoryEditView(generic.UpdateView, EventDraftStateMixin,
                          AccountMixin):
    form_class = forms.LotCategoryForm
    model = forms.LotCategoryForm.Meta.model
    template_name = 'lotcategory/form.html'
    event = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        else:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('subscription:category-list', kwargs={
            'event_pk': self.event.pk,
        })

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context.update(self.get_event_state_context_data(self.event))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'event': self.event})
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Categoria de lote alterada com sucesso.'
        )
        return response


class LotCategoryDeleteView(DeleteViewMixin, EventDraftStateMixin,):
    model = LotCategory
    delete_message = "Tem certeza que deseja excluir a categoria \"{name}\"?"
    success_message = "Categoria excluída com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_event_state_context_data(self.object.event))
        return context

    def get_success_url(self):
        return reverse(
            'subscription:category-list',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_delete(self):
        obj = self.get_object()
        return obj.is_deletable()
