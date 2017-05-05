from gatheros_event.lib.model.deletable import NotDeletableError
from django.views.generic import DeleteView
from django.contrib import messages


class DeleteViewMixin(DeleteView):
    protected = False
    message = None
    delete_message = ''

    def get_context_data( self, **kwargs ):
        context = super(DeleteViewMixin, self).get_context_data(**kwargs)
        context['protected'] = self.protected
        context['delete_message'] = self.delete_message.format(**self.object.__dict__)
        context['model_name'] = self.object._meta.verbose_name
        context['messages'] = messages.get_messages(self.request)

        return context

    def get_object( self, queryset=None ):
        obj = super(DeleteViewMixin, self).get_object(queryset=queryset)

        try:
            obj.check_deletable()
        except NotDeletableError:
            self.protected = True

        return obj

    def post( self, request, *args, **kwargs ):
        response = self.delete(request, *args, **kwargs)
        messages.success(request, "Evento excluído com sucesso!")
        return response
