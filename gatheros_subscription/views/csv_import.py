import csv

from django.contrib import messages
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from csv_importer.forms import CSVFileForm, CSVForm
from csv_importer.models import CSVImportFile
from .subscription import EventViewMixin

allowed_keys = [
    'nome',
    'email',
    'data nasc',
    'cpf',
    'doc internacional',
    'cep',
    'bairro',
    'número',
    'rua/logradouro',
    'complemento',
    'cidade'
    'uf',
    'celular',
    'função/cargo',
    'cnpj',
    'instituição/empresa',
    'status',
    'credenciado',
]


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


class CSVProcessView(CSVViewMixin, generic.DetailView):
    template_name = "subscription/csv_process.html"

    prefix = None
    initial = {}
    object = None

    def get_object(self, queryset=None):
        return CSVImportFile.objects.get(
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso.')
            return self.render_to_response(self.get_context_data())
        else:
            return self.form_invalid(form)

    def get_form(self):
        """Return an instance of the form to be used in this view."""
        return CSVForm(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'instance': self.object,
        }

        # A file in the POST dict and no file in the FILES dicts can cause a
        # form to not validate correctly, that is why we need this
        # treatment/cleanup.
        if 'csv_file' not in self.request.FILES and \
                'csv_file' in self.request.POST:
            self.request.POST._mutable = True
            del self.request.POST['csv_file']
            self.request.POST._mutable = False

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        messages.error(self.request, "Erro ao salvar configurações")
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def get_context_data(self, **kwargs):

        form = kwargs.pop('form', None)

        context = super().get_context_data(**kwargs)

        if form is None:
            form = CSVForm(instance=self.object)

        context['preview'] = self.get_preview()
        context['form'] = form
        return context

    def get_preview(self) -> dict:

        instance = self.object

        encoding = instance.encoding
        delimiter = instance.delimiter
        quotechar = instance.separator

        file_content = instance.csv_file.file.read()
        try:
            encoded_content = file_content.decode(encoding)
        except UnicodeDecodeError:
            return {
                'table': '<div class="text-center"><h2><strong>Não foi '
                         'possivel fazer a decodificação!</strong></h2></div>',
                'invalid_keys': None,
            }

        parsed_dict = self.parse_file(encoded_content, delimiter, quotechar)

        # TODO: this is not DRY
        content = encoded_content.splitlines()

        first_line = content[0].split(delimiter)

        table_keys = self.validate_table_keys(first_line)

        invalid_keys = []

        for entry in table_keys.items():
            if not entry[1]['valid']:
                invalid_keys.append(entry[1]['name'])

        table_heading = ''
        table_body = ''

        for key in parsed_dict.keys():
            table_heading += '<th>' + key.title() + '</th>'

        all_items_list = []

        for item in parsed_dict.items():
            # Limiting list size to not overload the frontend.  
            parsed_list = item[1][:20]

            all_items_list.append(parsed_list)

        all_rows = zip(*all_items_list)

        for row in all_rows:
            table_body += '<tr>'
            for item in row:
                table_body += '<td>'

                multi_item = item.split(delimiter)

                if len(multi_item) > 1:
                    table_body += '<ul>'

                    for i in multi_item:
                        table_body += '<li>' + i + '</li>'

                    table_body += '</ul>'

                else:
                    table_body += item

                table_body += '</td>'
            table_body += '</tr>'

        table = '<table class="table"><thead><tr>' + \
                table_heading + '</tr></thead><tbody>' + table_body + \
                '</tbody></table>'

        return {
            'table': table,
            'invalid_keys': invalid_keys,
        }

    def parse_file(self, encoded_content: str, delimiter: str, quotechar: str):

        content = encoded_content.splitlines()

        first_line = content[0].split(delimiter)

        table_keys = self.validate_table_keys(first_line)

        valid_keys = []

        for entry in table_keys.items():
            if entry[1]['valid']:
                valid_keys.append(entry[1]['name'])

        main_dict = {}
        for key in valid_keys:
            main_dict[key] = []

        reader = csv.DictReader(
            content,
            delimiter=delimiter,
            quotechar=quotechar,
        )

        for row in reader:
            for item in row.items():

                possible_key = item[0].lower().strip()
                possible_value = item[1].strip()

                if possible_value and possible_key in valid_keys:
                    main_dict[possible_key].append(possible_value)

        return main_dict

    @staticmethod
    def validate_table_keys(line: list) -> dict:

        main_dict = {}

        for key in line:

            lower_key = key.lower().strip()
            is_valid = False
            index = line.index(key)

            if lower_key in allowed_keys:
                is_valid = True
                key = lower_key

            current_dict = {
                'valid': is_valid,
                'name': key,
            }

            main_dict.update({index: current_dict})

        return main_dict

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
