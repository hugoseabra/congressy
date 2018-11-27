from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from gatheros_subscription.models import Lot
from importer.forms import (
    CSVFileForm,
    CSVFileConfigForm,
    CSVProcessForm,
    CSVCityForm,
)
from importer.helpers import (
    get_keys_mapping_dict,
    get_survey_questions,
)
from importer.line_data import (
    LineDataCollection,
    LineDataCollectionBuilder,
    NoValidLinesError,
)
from importer.models import CSVFileConfig
from importer.persistence import (
    CSVErrorPersister,
    XLSErrorPersister,
    XLSLotExamplePersister,
    CSVCorrectionPersister,
    CSVCityCorrectionPersister,
)
from importer.preview_builder import PreviewBuilder
from importer.question_mapping import QuestionMapping
from .mixins import CSVViewMixin, CSVProcessedViewMixin


class CSVListView(CSVViewMixin, generic.ListView):
    """
        View responsavel por fazer a listagem dos arquivos CSV de determinado
        evento e de engatilhar novas importações.
    """
    template_name = "importer/csv_file_list.html"

    def get_queryset(self):
        return CSVFileConfig.objects.filter(event=self.event)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CSVFileForm(initial={'event': self.event.pk})
        return context


class CSVFileImportView(CSVViewMixin, generic.FormView):
    """
        View usada para fazer apenas upload de arquivos
    """
    template_name = "importer/csv_upload.html"
    object = None

    def get_form(self, form_class=None):

        kwargs = self.get_form_kwargs()
        kwargs['initial'] = {'event': self.event.pk}

        return CSVFileForm(**kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'importer:csv-file-prepare',
            kwargs={
                'csv_pk': self.object.pk,
                'event_pk': self.event.pk,
            }
        )

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Arquivo submetido com sucesso!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        for error, value in form.errors.items():

            if error == 'csv_file':
                error = "Arquivo CSV"

            messages.error(self.request,
                           "{}: {}".format(error, value[0]))

        return self.render_to_response(self.get_context_data(form=form))


class CSVExampleFileView(CSVViewMixin, generic.View):
    lot = None

    def dispatch(self, request, *args, **kwargs):
        self.lot = get_object_or_404(
            Lot,
            pk=self.kwargs.get('lot_pk'),
            event=self.kwargs.get('event_pk'),
        )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        xls = self._create_xls()

        response = HttpResponse(xls, content_type=self._get_mime_type())
        response[
            'Content-Disposition'] = 'attachment; filename="{}"'.format(
            'Exemplo_' + self.lot.name + '.xls',
        )

        return response

    def _create_xls(self) -> bytes:
        xls_maker = XLSLotExamplePersister(lot=self.lot)
        return xls_maker.make()

    @staticmethod
    def _get_mime_type() -> str:
        mime = 'application'
        content_type = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return '{}/{}'.format(mime, content_type)


class CSVPrepareView(CSVProcessedViewMixin):
    template_name = "importer/csv_prepare.html"
    initial = {}
    prefix = None

    def get_context_data(self, **kwargs):

        form = kwargs.pop('form', None)
        context = super().get_context_data(**kwargs)

        if form is None:
            form = CSVFileConfigForm(instance=self.object)

        context['key_mapping'] = self.get_key_mappings()
        context['questions'] = self.get_survey_questions()

        preview_table = None
        denied_reason = None
        invalid_keys = None

        try:
            preview_table = self.get_html_preview_table()
            invalid_keys = self.get_invalid_keys()
        except UnicodeDecodeError:
            denied_reason = "Não foi possivel decodificar seu arquivo!"
        except NoValidLinesError:
            denied_reason = "Seu arquivo não possui nenhuma linha válida"

        context['form'] = form
        context['has_inside_bar'] = False
        context['preview_table'] = preview_table
        context['denied_reason'] = denied_reason
        context['invalid_keys'] = invalid_keys

        return context

    def get_key_mappings(self) -> list:
        form_config = self.object.lot.event.formconfig
        return get_keys_mapping_dict(form_config=form_config)

    def get_survey_questions(self) -> list:

        survey_key_questions = list()

        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey
            all_questions = get_survey_questions(survey)
            for question in all_questions:
                survey_key_questions.append(QuestionMapping(question))

        return survey_key_questions

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

    # --------- CUSTOM --------------
    def get_data_collection(self, size):

        file_path = self.object.csv_file.path
        delimiter = self.object.delimiter
        separator = self.object.separator
        encoding = self.object.encoding

        return LineDataCollectionBuilder(
            file_path=file_path,
            delimiter=delimiter,
            separator=separator,
            encoding=encoding,
        ).get_collection(size)

    def get_html_preview_table(self) -> str:

        previewer = PreviewBuilder(
            ldc=self.get_data_collection(size=25),
            lot=self.object.lot,
        )

        return previewer.render_html_table()

    def get_invalid_keys(self):
        line_data_collection = self.get_data_collection(size=1)
        invalid = list()

        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey
            invalid = line_data_collection[0].get_invalid_keys(survey)

        return invalid


class CSVErrorXLSView(CSVViewMixin):
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        xls = self._create_xls()

        response = HttpResponse(xls, content_type=self._get_mime_type())
        response[
            'Content-Disposition'] = 'attachment; filename="{}"'.format(
            self.object.err_filename().split('.')[0] + '.xls',
        )

        return response

    def _create_xls(self) -> bytes:
        error_csv = self.object.error_csv_file.path
        survey = None
        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey
        xls_maker = XLSErrorPersister(error_csv)
        return xls_maker.make(survey)

    def get_object(self, queryset=None):
        return get_object_or_404(
            CSVFileConfig,
            pk=self.kwargs.get('csv_pk'),
            event=self.kwargs.get('event_pk'),
        )

    @staticmethod
    def _get_mime_type() -> str:
        mime = 'application'
        content_type = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return '{}/{}'.format(mime, content_type)


class CSVDeleteView(CSVProcessedViewMixin, generic.DeleteView):

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Arquivo apagado com sucesso!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('importer:csv-list', kwargs={
            'event_pk': self.event.pk
        })


class CSVProcessView(CSVProcessedViewMixin, generic.FormView):
    template_name = 'importer/csv_process.html'
    form_class = CSVProcessForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Redirect to fix cities
        if self._check_for_invalid_cities():
            return redirect(reverse_lazy('importer:csv-fix-cities', kwargs={
                'event_pk': self.event.pk,
                'csv_pk': self.object.pk,
            }))

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        context['process_results'] = self.process()

        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        create_subs = cleaned_data.get('create_subscriptions')

        if create_subs:
            results = self.process(commit=True)
            self.object.processed = True
            self.object.save()

            messages.success(self.request,
                             "Criadas {} inscrições com sucesso".format(
                                 results['valid']))

            return redirect(self.get_success_url())

    def form_invalid(self, form):

        for field, errs in form.errors.items():
            for err in errs:
                messages.error(self.request, 'Erro: {}: {}'.format(field, err))

        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('importer:csv-list', kwargs={
            'event_pk': self.event.pk
        })

    def process(self, commit: bool = False) -> dict:
        line_data_persistence_collection = self.get_data_collection()

        valid_lines_list = LineDataCollection()
        invalid_lines_list = LineDataCollection()

        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey
        else:
            survey = None

        for line in line_data_persistence_collection:
            line.save(commit=commit,
                      form_config=self.object.lot.event.formconfig,
                      survey=survey,
                      lot=self.object.lot, user=self.request.user)

            if line.has_errors():
                invalid_lines_list.append(line)
            else:
                valid_lines_list.append(line)

        if invalid_lines_list:
            self._create_error_csv(invalid_lines_list)

        return {
            'valid': len(valid_lines_list),
            'invalid': len(invalid_lines_list),
            'valid_list': valid_lines_list,
            'invalid_list': invalid_lines_list,
        }

    def get_data_collection(self):

        if self.object.correction_csv_file:
            file_path = self.object.correction_csv_file.path
        else:
            file_path = self.object.csv_file.path

        delimiter = self.object.delimiter
        separator = self.object.separator
        encoding = self.object.encoding

        return LineDataCollectionBuilder(
            file_path=file_path,
            delimiter=delimiter,
            separator=separator,
            encoding=encoding,
        ).get_collection()

    def _create_error_csv(self, line_data_collection: LineDataCollection):

        # Creating file in filesystem
        survey = None
        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey
        csvfile = CSVErrorPersister(line_data_collection).write(survey)

        # Saving a reference to the file
        self.object.error_csv_file.save(self.object.filename(), csvfile)

    def _check_for_invalid_cities(self):
        line_data_persistence_collection = self.get_data_collection()

        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey
        else:
            survey = None

        for line in line_data_persistence_collection:

            line.save(commit=False,
                      form_config=self.object.lot.event.formconfig,
                      survey=survey,
                      lot=self.object.lot, user=self.request.user)

            errors = line.get_errors()

            if errors:
                # Test if only has city error
                if len(errors) == 1 and 'city' in errors:
                    return True

        return False

    @staticmethod
    def _get_mime_type() -> str:
        mime = 'application'
        content_type = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return '{}/{}'.format(mime, content_type)


class CSVFixCitiesView(CSVProcessedViewMixin, generic.FormView):
    template_name = 'importer/fix_cities.html'
    form_class = CSVCityForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.correction_csv_file:
            self._create_correction_csv()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        invalid_city = self.get_invalid_city_line()
        context['invalid_city'] = invalid_city

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        invalid_city = self.get_invalid_city_line()

        if invalid_city:
            survey = None
            if self.object.lot.event_survey:
                survey = self.object.lot.event_survey.survey

            csvfile = CSVCityCorrectionPersister(
                old=invalid_city,
                new=form.cleaned_data['city'],
                line_data_collection=self.get_data_collection(raw=False)
            ).write(survey)

            self.object.correction_csv_file.save(self.object.filename(),
                                                 csvfile)

        if self.get_invalid_city_line():
            messages.success(self.request,
                             "Cidade corrigida com sucesso!")
            return redirect(reverse_lazy('importer:csv-fix-cities',
                                         kwargs={
                                             'event_pk': self.event.pk,
                                             'csv_pk': self.object.pk,
                                         }))

        messages.success(self.request,
                         "Todas as cidades corrigidas com sucesso!")
        return redirect(reverse_lazy('importer:csv-file-process', kwargs={
            'event_pk': self.event.pk,
            'csv_pk': self.object.pk,
        }))

    def form_invalid(self, form):
        print('breakpoint')
        return super().form_invalid(form)

    # ------- CUSTOM ------------

    def get_invalid_city_line(self):

        line_data_persistence_collection = self.get_data_collection(raw=False)

        for line in line_data_persistence_collection:

            line.save(commit=False,
                      form_config=self.object.lot.event.formconfig,
                      lot=self.object.lot, user=self.request.user)

            errors = line.get_errors()

            if errors:
                # Test if only has city error
                if len(errors) == 1 and 'city' in errors:
                    return line.city

        return None

    def get_data_collection(self, size: int = 0, raw: bool = True):

        if raw:
            file_path = self.object.csv_file.path
        else:
            file_path = self.object.correction_csv_file.path

        delimiter = self.object.delimiter
        separator = self.object.separator
        encoding = self.object.encoding

        return LineDataCollectionBuilder(
            file_path=file_path,
            delimiter=delimiter,
            separator=separator,
            encoding=encoding,
        ).get_collection(size)

    def _create_correction_csv(self):
        survey = None
        if self.object.lot.event_survey:
            survey = self.object.lot.event_survey.survey

        csvfile = CSVCorrectionPersister(self.get_data_collection()).write(
            survey)
        self.object.correction_csv_file.save(self.object.filename(), csvfile)
