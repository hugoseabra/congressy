from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from csv_importer.forms import CSVFileForm, CSVFileConfigForm, CSVProcessForm
from csv_importer.models import CSVFileConfig
from subscription_importer import (
    CSVFormIntegrator,
    DataFileTransformer,
    PreviewFactory,
    NoValidColumnsError,
    NoValidLinesError,
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
        lot_pk = self.object.lot.pk
        return CSVFormIntegrator(lot_pk).get_required_keys()

    def get_preview(self) -> tuple:

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

        preview_factory = PreviewFactory(data_transformer.get_lines(size=3))

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

        return context

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
