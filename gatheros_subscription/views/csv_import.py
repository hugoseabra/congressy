from django.contrib import messages
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from csv_importer.forms import CSVFileForm, CSVForm
from csv_importer.models import CSVImportFile
from .helpers import validate_table_keys, parse_file, KEY_MAP
from .subscription import EventViewMixin
from gatheros_subscription.models import Subscription


class CannotGeneratePreviewError(Exception):
    pass


class CannotCreateSubscriptionsError(Exception):
    pass


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'inscricoes'
        return context


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
        context['supported_keys'] = KEY_MAP
        return context


class CSVImportView(CSVViewMixin, generic.View):
    """
        View usada para fazer upload de arquivos.
    """
    form_class = CSVFileForm
    initial = {}
    prefix = None

    def get_success_url(self):
        return reverse_lazy('subscription:subscriptions-csv-list', kwargs={
            'event_pk': self.event.pk
        })

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Arquivo submetido com sucesso!")
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        return HttpResponse("Método não permitido.", status=405)

    def put(self, *args, **kwargs):
        return HttpResponse("Método não permitido.", status=405)

    def post(self, request, *args, **kwargs):
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
                           "Erro no campo {}: {}".format(error, value[0]))

        return redirect(self.get_success_url())


class CSVPrepareView(CSVViewMixin, generic.DetailView):
    template_name = "subscription/csv_prepare.html"

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

        context['denied_reason'] = None
        context['preview'] = None
        context['has_inside_bar'] = False
        context['supported_keys'] = KEY_MAP

        try:
            context['preview'] = self.get_preview()
        except CannotGeneratePreviewError as e:

            if str(e) == 'Decode error':
                context['denied_reason'] = 'Não foi possivel ' \
                                           'fazer a decodificação do arquivo! Verifique o tipo de encodificação.'
            else:
                context['denied_reason'] = str(e)

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

            raise CannotGeneratePreviewError("Decode error")

        parsed_dict = parse_file(encoded_content, delimiter, quotechar)

        # TODO: this is not DRY
        content = encoded_content.splitlines()

        first_line = content[0].split(delimiter)

        table_keys = validate_table_keys(first_line)

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
            parsed_list = item[1][:10]

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


class CSVProcessView(CSVViewMixin, generic.DetailView):
    template_name = "subscription/csv_process.html"
    object = None
    preview = None

    required_keys = [
        'email',
        'nome',
    ]

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.preview is None:
            self.preview = self.get_preview()
        return response

    def get_preview(self) -> dict:

        instance = self.object

        encoding = instance.encoding
        delimiter = instance.delimiter
        quotechar = instance.separator

        file_content = instance.csv_file.file.read()
        try:
            encoded_content = file_content.decode(encoding)
        except UnicodeDecodeError:
            raise CannotGeneratePreviewError("Decode error")

        return parse_file(encoded_content, delimiter, quotechar)

    def get_object(self, queryset=None):
        return CSVImportFile.objects.get(
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['possible_subscriptions'] = 0
        context['denied_reason'] = None

        try:
            context['possible_subscriptions'] = \
                self.get_possible_subscriptions()
        except CannotCreateSubscriptionsError as e:
            context['denied_reason'] = str(e)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        raise NotImplementedError('POST NOT READY')

    def get_possible_subscriptions(self) -> int:

        if self.object is None:
            raise CannotCreateSubscriptionsError(
                'Não foi possivel pegar o arquivo.'
            )

        if self.preview is None:
            self.preview = self.get_preview()
            if self.preview is None:
                raise CannotCreateSubscriptionsError(
                    'Não foi possivel processar seu arquivo.'
                )

        for key in self.required_keys:
            if key not in self.preview:
                msg = 'Não será possivel gerar inscrições sem o ' \
                      'campo {}.'.format(key.title())
                raise CannotCreateSubscriptionsError(msg)

        possible_subscriptions = 0

        return possible_subscriptions
