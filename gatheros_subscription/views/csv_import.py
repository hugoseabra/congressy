from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from csv_importer.forms import CSVFileForm
from csv_importer.models import CSVFileConfig
from subscription_importer import (
    KEY_MAP,
    CSVFormIntegrator,
    DataFileTransformer,
    ColumnValidator,
    MappingNotFoundError,
    NoValidColumnsError,
)
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

                url = reverse_lazy(
                    "subscription:subscription-list",
                    kwargs={
                        'event_pk': self.event.pk
                    }
                )

                return redirect(url)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'
        return context


class CSVFileListView(CSVViewMixin, generic.ListView):
    """
        View responsavel por fazer a listagem dos arquivos CSV de determinado
        evento e de engatilhar novas importações.
    """
    template_name = "subscription/csv_file_list.html"

    def get_queryset(self):
        return CSVFileConfig.objects.filter(event=self.event)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CSVFileForm(initial={'event': self.event.pk})
        return context


class CSVImportView(CSVViewMixin, generic.View):
    """
        View usada para fazer apenas upload de arquivos via POST, qualquer outra
        solicitação irá gerar um HTTP 403.
    """
    form_class = CSVFileForm
    initial = {}
    prefix = None
    http_method_names = ['post']

    def get_success_url(self):
        return reverse_lazy('subscription:subscriptions-csv-list', kwargs={
            'event_pk': self.event.pk
        })

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Arquivo submetido com sucesso!")
        return redirect(self.get_success_url())

    def post(self, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        for error, value in form.errors.items():
            messages.error(self.request,
                           "{}: {}".format(error, value[0]))

        return redirect(self.get_success_url())


class CSVPrepareView(CSVViewMixin, generic.DetailView):
    template_name = "subscription/csv_prepare.html"

    def get_object(self, queryset=None):
        return CSVFileConfig.objects.get(
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['required_keys'] = self.get_required_keys()

        preview = None
        denied_reason = None
        invalid_keys = None

        try:
            preview = self.get_preview()
        except UnicodeDecodeError:
            denied_reason = "Não foi possivel decodificar seu arquivo!"
        except NoValidColumnsError as e:
            invalid_keys = e.column_validator.invalid_keys
            denied_reason = "Seu arquivo não possui nenhum campo valido!"

        context['preview'] = preview
        context['denied_reason'] = denied_reason
        context['invalid_keys'] = invalid_keys

        return context

    def get_required_keys(self) -> list:
        required_keys_mapping = []
        lot_pk = self.object.lot.pk

        required_keys_list = CSVFormIntegrator(lot_pk).get_required_keys()

        for key in required_keys_list:
            mapping = KEY_MAP.get(key, None)
            if mapping is None:
                raise MappingNotFoundError(key)
            required_keys_mapping.append(mapping)

        return required_keys_mapping

    def get_preview(self) -> dict:

        file_path = self.object.csv_file.path
        delimiter = self.object.delimiter
        separator = self.object.separator
        encoding = self.object.encoding

        data_transformer = DataFileTransformer(
            file_path=file_path,
            delimiter=delimiter,
            separator=separator,
            encoding=encoding,
        )

        # Validating columns
        column_validator = ColumnValidator(data_transformer.get_columns())

        if not column_validator.has_valid():
            raise NoValidColumnsError(column_validator)

        valid_keys = column_validator.valid_columns

        # Validating lines lines
        dict_list = data_transformer.get_dict_list(size=50)
        valid_lines = []
        for line in dict_list:
            print('assd')




#
#     def post(self, request, *args, **kwargs):
#         """
#         Handle POST requests: instantiate a form instance with the passed
#         POST variables and then check if it's valid.
#         """
#         self.object = self.get_object()
#         form = self.get_form()
#
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Configurações salvas com sucesso.')
#             return self.render_to_response(self.get_context_data())
#         else:
#             return self.form_invalid(form)
#
#     def get_form(self):
#         """Return an instance of the form to be used in this view."""
#         return CSVForm(**self.get_form_kwargs())
#
#     def get_form_kwargs(self):
#         """Return the keyword arguments for instantiating the form."""
#         kwargs = {
#             'initial': self.get_initial(),
#             'prefix': self.get_prefix(),
#             'instance': self.object,
#         }
#
#         # A file in the POST dict and no file in the FILES dicts can cause a
#         # form to not validate correctly, that is why we need this
#         # treatment/cleanup.
#         if 'csv_file' not in self.request.FILES and \
#                 'csv_file' in self.request.POST:
#             self.request.POST._mutable = True
#             del self.request.POST['csv_file']
#             self.request.POST._mutable = False
#
#         if self.request.method in ('POST', 'PUT'):
#             kwargs.update({
#                 'data': self.request.POST,
#                 'files': self.request.FILES,
#             })
#         return kwargs
#
#     def form_invalid(self, form):
#         """If the form is invalid, render the invalid form."""
#         messages.error(self.request, "Erro ao salvar configurações")
#         return self.render_to_response(self.get_context_data(form=form))
#
#     def get_initial(self):
#         """Return the initial data to use for forms on this view."""
#         return self.initial.copy()
#
#     def get_prefix(self):
#         """Return the prefix to use for forms."""
#         return self.prefix
#
#     def get_context_data(self, **kwargs):
#
#         form = kwargs.pop('form', None)
#
#         context = super().get_context_data(**kwargs)
#
#         if form is None:
#             form = CSVForm(instance=self.object)
#
#         context['denied_reason'] = None
#         context['preview'] = None
#         context['has_inside_bar'] = False
#         context['supported_keys'] = KEY_MAP
#
#         try:
#             context['preview'] = self.get_preview()
#         except CannotGeneratePreviewError as e:
#
#             if str(e) == 'Decode error':
#                 context['denied_reason'] = 'Não foi possivel ' \
#                                            'fazer a decodificação do arquivo! Verifique o tipo de encodificação.'
#             else:
#                 context['denied_reason'] = str(e)
#
#         context['form'] = form
#         return context
#
#     def get_preview(self) -> dict:
#
#         serialized_csv = self.get_serialized_csv()
#
#         # Fetching invalid keys
#         invalid_keys = self.get_invalid_keys(serialized_csv['table_keys'])
#
#         # Fetching valid keys
#         valid_keys = self.get_valid_keys(serialized_csv['table_keys'])
#
#         # Fetching valid lines
#         valid_lines = self.get_valid_lines(serialized_csv['csv_dict_list'])
#
#         table = None
#
#         if valid_keys and valid_lines:
#
#             table_heading = ''
#             table_body = ''
#
#             for key in valid_keys:
#                 table_heading += '<th>' + key.title() + '</th>'
#
#
#
#
#             table = '<table class="table"><thead><tr>' + \
#                     table_heading + '</tr></thead><tbody>' + table_body + \
#                     '</tbody></table>'
#
#         return {
#             'table': table,
#             'invalid_keys': invalid_keys,
#         }
#
#     def get_serialized_csv(self) -> dict:
#
#         instance = self.object
#
#         encoding = instance.encoding
#         delimiter = instance.delimiter
#         quotechar = instance.separator
#         file_path = instance.csv_file.path
#
#         # Decoding and marshalling into a list of dicts
#         try:
#             reader = csv.DictReader(
#                 open(file_path, 'r', encoding=encoding),
#                 delimiter=delimiter,
#                 quotechar=quotechar,
#             )
#             dict_list = []
#             for line in reader:
#                 dict_list.append(line)
#             table_keys = reader.fieldnames
#         except UnicodeDecodeError:
#             raise CannotGeneratePreviewError("Decode error")
#
#         return {
#             'csv_dict_list': dict_list,
#             'table_keys': table_keys,
#         }
#
#     def get_valid_lines(self, csv_dict_list: list):
#
#         valid_lines = []
#
#         for line in csv_dict_list:
#             is_valid = self.is_valid_line(line)
#             if is_valid:
#                 valid_lines.append(line)
#
#         return valid_lines
#
#     @staticmethod
#     def get_invalid_keys(table_keys: list) -> list:
#
#         invalid_keys = []
#         for entry in table_keys:
#
#             is_valid = False
#
#             parsed_entry = entry.lower().strip()
#
#             for key, value in KEY_MAP.items():
#                 if parsed_entry in value['csv_keys']:
#                     is_valid = True
#                     break
#
#             if not is_valid:
#                 invalid_keys.append(entry)
#
#         return invalid_keys
#
#     @staticmethod
#     def get_valid_keys(table_keys: list) -> list:
#
#         valid_keys = []
#         for entry in table_keys:
#
#             is_valid = False
#
#             parsed_entry = entry.lower().strip()
#
#             for key, value in KEY_MAP.items():
#                 if parsed_entry in value['csv_keys']:
#                     is_valid = True
#                     break
#
#             if is_valid:
#                 valid_keys.append(entry)
#
#         return valid_keys
#
#     @staticmethod
#     def is_valid_line(line: OrderedDict) -> bool:
#
#         line_keys = [key.lower().strip() for key in line.keys()]
#         line_mapping_keys = []
#
#         for key in line_keys:
#             mapping_key = False
#             try:
#                 mapping_key, _ = get_mapping_key_from_csv_key(key)
#             except MappingNotFoundError:
#                 pass
#
#             if mapping_key:
#                 line_mapping_keys.append(mapping_key)
#
#         for key in REQUIRED_KEYS:
#             if key not in line_mapping_keys:
#                 return False
#
#         return True
#
#
# class CSVProcessView(CSVViewMixin, generic.DetailView):
#     template_name = "subscription/csv_process.html"
#     object = None
#     preview = None
#
#     # Must be a key from the KEY_MAP
#     required_keys = [
#         'email',
#         'name',
#     ]
#
#     def dispatch(self, request, *args, **kwargs):
#         response = super().dispatch(request, *args, **kwargs)
#         if self.preview is None:
#             self.preview = self.get_preview()
#         return response
#
#     def get_preview(self) -> dict:
#
#         instance = self.object
#
#         encoding = instance.encoding
#         delimiter = instance.delimiter
#         quotechar = instance.separator
#
#         file_content = instance.csv_file.file.read()
#         try:
#             encoded_content = file_content.decode(encoding)
#         except UnicodeDecodeError:
#             raise CannotGeneratePreviewError("Decode error")
#
#         return parse_file(encoded_content, delimiter, quotechar)
#
#     def get_object(self, queryset=None):
#         return CSVImportFile.objects.get(
#             pk=self.kwargs.get('csv_pk'),
#             event=self.kwargs.get('event_pk'),
#         )
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['possible_subscriptions'] = 0
#         context['denied_reason'] = None
#
#         try:
#             context['generated_subscriptions'] = \
#                 self.generate_subscriptions()
#         except CannotCreateSubscriptionsError as e:
#             context['denied_reason'] = str(e)
#
#         return context
#
#     def post(self, request, *args, **kwargs):
#         return HttpResponse("Método não permitido", status=403)
#
#     def generate_subscriptions(self) -> dict:
#
#         if self.object is None:
#             raise CannotCreateSubscriptionsError(
#                 'Não foi possivel pegar o arquivo.'
#             )
#
#         if self.preview is None:
#             self.preview = self.get_preview()
#             if self.preview is None:
#                 raise CannotCreateSubscriptionsError(
#                     'Não foi possivel processar seu arquivo.'
#                 )
#
#         for key in self.required_keys:
#             if key not in self.preview:
#                 msg = 'Não será possivel gerar inscrições sem o ' \
#                       'campo {}.'.format(key.title())
#                 raise CannotCreateSubscriptionsError(msg)
#
#         subscriptions = {
#             'total_subscriptions': 15,
#             'successful_subscriptions': 2,
#             'failed_subscriptions': 13,
#         }
#
#         return subscriptions
