from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from csv_importer.forms import CSVFileForm, CSVFileConfigForm, CSVProcessForm
from csv_importer.models import CSVFileConfig
from subscription_importer import (
    DataFileTransformer,
    PreviewFactory,
    NoValidColumnsError,
    NoValidLinesError,
    LineData,
    get_required_keys_mappings,
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


class CSVListView(CSVViewMixin, generic.ListView):
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


class CSVFileImportView(CSVViewMixin, generic.View):
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
    initial = {}
    prefix = None
    object = None

    def get_object(self, queryset=None):
        return CSVFileConfig.objects.get(
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )

    def get_context_data(self, **kwargs):

        form = kwargs.pop('form', None)
        context = super().get_context_data(**kwargs)

        if form is None:
            form = CSVFileConfigForm(instance=self.object)

        context['required_keys'] = self.get_required_keys()

        preview_table = None
        denied_reason = None
        invalid_keys = None

        try:
            preview_table, invalid_keys = self.get_preview()
        except UnicodeDecodeError:
            denied_reason = "Não foi possivel decodificar seu arquivo!"
        except NoValidColumnsError as e:
            invalid_keys = e.line_data.get_invalid_keys()
            denied_reason = "Seu arquivo não possui nenhum campo válido!"
        except NoValidLinesError:
            denied_reason = "Seu arquivo não possui nenhuma linha válida"

        context['form'] = form
        context['has_inside_bar'] = False
        context['preview_table'] = preview_table
        context['denied_reason'] = denied_reason
        context['invalid_keys'] = invalid_keys

        return context

    def get_required_keys(self) -> list:
        form_config = self.object.lot.event.formconfig
        return get_required_keys_mappings(form_config=form_config)

    def get_transformer(self):

        file_path = self.object.csv_file.path
        delimiter = self.object.delimiter
        separator = self.object.separator
        encoding = self.object.encoding

        return DataFileTransformer(
            file_path=file_path,
            delimiter=delimiter,
            separator=separator,
            encoding=encoding,
        )

    def get_preview(self) -> tuple:

        transformer = self.get_transformer()

        preview_factory = PreviewFactory(transformer.get_lines(size=3))

        return preview_factory.table, preview_factory.invalid_keys

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
        return CSVFileConfigForm(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'instance': self.object,
        }

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


class CSVProcessView(CSVViewMixin, generic.FormView):
    template_name = 'subscription/csv_process.html'
    form_class = CSVProcessForm
    object = None

    def get_object(self):
        return CSVFileConfig.objects.get(
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        context['process_results'] = self.process()

        return context

    def get_transformer(self):
        file_path = self.object.csv_file.path
        delimiter = self.object.delimiter
        separator = self.object.separator
        encoding = self.object.encoding

        return DataFileTransformer(
            file_path=file_path,
            delimiter=delimiter,
            separator=separator,
            encoding=encoding,
        )

    def process(self, commit: bool = False) -> dict:
        raw_data_list = self.get_transformer().get_lines()

        valid_line_counter = 0
        invalid_line_counter = 0
        invalid_lines_list = []

        for line in raw_data_list:

            line_data = LineData(line)
            line_data.save(commit=commit,
                           form_config=self.event.formconfig,
                           lot=self.object.lot, user=self.request.user)

            if line_data.is_valid():
                valid_line_counter += 1
            else:
                invalid_line_counter += 1
                invalid_lines_list.append(line_data)

        if len(invalid_lines_list) > 0:
            self._create_error_csv(invalid_lines_list)
            self._create_error_xls(invalid_lines_list)

        return {
            'valid': valid_line_counter,
            'invalid': invalid_line_counter,
        }

    def _create_error_csv(self, data_line_list: list):
        pass

    def _create_error_xls(self, data_line_list: list):
        pass
