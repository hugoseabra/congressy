from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.views.mixins import DeleteViewMixin, \
    MultiLotsFeatureFlagMixin
from gatheros_subscription import forms
from gatheros_subscription.models import LotCategory

try:
    from raven.contrib.django.raven_compat.models import client

    SENTRY_RAVEN = True

except ImportError:
    SENTRY_RAVEN = False


class LotCategoryListView(generic.ListView):
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
        return context

    def get_queryset(self):
        """Lotes a exibir são de acordo com o evento e não-interno"""
        query_set = super().get_queryset()
        query_set = query_set.filter(event=self.event)

        if not self.event.feature_configuration.feature_multi_lots:
            cats_with_active_lots = query_set.filter(
                lots__active=True
            )
            if cats_with_active_lots.count() == 0:
                cats_with_active_lots = query_set
                if SENTRY_RAVEN:
                    message = 'Nenhuma categoria com lote ativo'
                    extra_data = {
                        'event_pk': self.event.pk,
                        'event': self.event.name,
                    }
                    client.captureMessage(message, **extra_data)
                else:
                    raise Exception('Nenhuma categoria com lote ativo')

            first = cats_with_active_lots.first()
            query_set = query_set.filter(pk=first.pk)

        return query_set.order_by('pk')


class LotCategoryAddView(MultiLotsFeatureFlagMixin, generic.CreateView):
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


class LotCategoryEditView(generic.UpdateView):
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


class LotCategoryDeleteView(DeleteViewMixin):
    model = LotCategory
    delete_message = "Tem certeza que deseja excluir a categoria \"{name}\"?"
    success_message = "Categoria excluída com sucesso!"

    def get_success_url(self):
        return reverse(
            'subscription:category-list',
            kwargs={'event_pk': self.kwargs['event_pk']}
        )

    def can_delete(self):
        obj = self.get_object()
        return obj.is_deletable()
