from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from csv_importer.forms import CSVForm, CSVFileForm
from csv_importer.models import CSVImportFile
from .subscription import EventViewMixin


class CSVViewMixin(EventViewMixin):
    """
        Mixin utilizado para não permitir acesso sem determinada flag ativada.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not self.event.allow_importing:

            if request.is_ajax():
                message = 'Evento não permite importação via CSV'
                return JsonResponse({'error': message}, status=403)

            else:

                messages.error(request,
                               "Evento não permite importação via CSV.")
                return redirect(
                    reverse_lazy("subscription:subscription-list",
                                 kwargs={
                                     'event_pk': self.event.pk
                                 })
                )

        return response


class CSVFileListView(CSVViewMixin, generic.ListView):
    """
        View responsavel por fazer a listagem dos arquivos CSV de determinado
        evento.
    """
    template_name = "subscription/csv_file_list.html"

    def get_queryset(self):
        return CSVImportFile.objects.filter(event=self.event)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CSVFileForm(initial={'event': self.event.pk})
        return context


class CSVImportView(CSVViewMixin, generic.FormView):
    """
        View usada para fazer upload de arquivos.
    """
    form_class = CSVFileForm

    def get_success_url(self):
        return reverse_lazy('subscription:subscriptions-csv-list', kwargs={
            'event_pk': self.event.pk
        })

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Arquivo submetido com sucesso!")
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        return HttpResponse("Método não permitido.", status=405)

    def put(self, *args, **kwargs):
        return HttpResponse("Método não permitido.", status=405)

class CSVConfigView(CSVViewMixin, generic.TemplateView):
    template_name = "subscription/csv_import.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CSVForm(initial={'event': self.event})
        return context
# class CSVImportView(CSVViewMixin, generic.FormView):
#     form_class = CSVForm
#     preview = False
#
#     def dispatch(self, request, *args, **kwargs):
#
#         if not request.is_ajax():
#             message = 'Apenas requisições do tipo XMLHttpRequest são ' \
#                       'permitidas.'
#             return JsonResponse({'error': message}, status=403)
#
#         is_preview = request.POST.get('preview', False)
#
#         if is_preview and is_preview == 'true':
#             self.preview = True
#
#         return super().dispatch(request, *args, **kwargs)
#
#     def form_valid(self, form):
#
#         instance = form.save()
#
#         encoding = form.cleaned_data['encoding']
#
#         file_content = instance.csv_file.file.read()
#
#         encoded_content = file_content.decode(encoding)
#
#         content = encoded_content.splitlines()
#
#         delimiter = form.cleaned_data['delimiter']
#         quotechar = form.cleaned_data['separator']
#
#         if self.preview:
#
#             all_lines = content.splitlines()
#
#             first_line = all_lines.pop(0)
#
#             table_keys = first_line.split(delimiter)
#
#             table_heading = ''
#             table_body = ''
#
#             for key in table_keys:
#                 table_heading += '<th>' + key + '</th>'
#
#             for line in all_lines:
#
#                 current_line = line.split(delimiter)
#
#                 table_body += '<tr>'
#
#                 for entry in current_line:
#                     entry = entry.strip()
#                     if entry:
#
#                         entry = entry.split(quotechar)
#                         table_body += '<td>'
#
#                         for item in entry:
#                             table_body += item
#
#                         table_body += '</td>'
#                     else:
#                         table_body += '<td> --- </td>'
#
#                 table_body += '</tr>'
#
#             html = '<table class="table"><thead><tr>' + \
#                    table_heading + '</tr></thead><tbody>' + table_body + \
#                    '</tbody></table>'
#
#             return HttpResponse(html)
#         else:
#             raise NotImplementedError()
#             # file_obj = ContentFile(, name=instance.csv_file.name)
#             # instance.csv_file = file_obj
#             # instance.save()
#
#             # TODO: Generate a redirect to confirm subscriptions.
#
#     def form_invalid(self, form):
#         return JsonResponse(dict(form.errors.items()))
