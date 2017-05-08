from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from core.view.user_context import UserContextViewMixin
from gatheros_event.models import Member
from .form_steps import EventFormStep1, EventFormStep2, EventFormStep3, \
    EventFormStep4


class EventAddView(LoginRequiredMixin, UserContextViewMixin, SessionWizardView):
    template_name = 'gatheros_event/event/add.html'

    form_list = [EventFormStep1, EventFormStep2, EventFormStep3, EventFormStep4]
    file_storage = FileSystemStorage(settings.MEDIA_ROOT)

    def render_to_response( self, context, **response_kwargs ):
        if not self.can_add():
            messages.success(
                self.request,
                "Você não tem permissão para adicionar evento"
            )
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventAddView, self).render_to_response(
            context=context,
            **response_kwargs
        )

    def can_add( self ):
        if self.user_context.get('superuser', False):
            return True

        active_member = self.user_context['active_member_group']
        return active_member and active_member['group'] == Member.ADMIN
