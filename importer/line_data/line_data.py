from collections import OrderedDict

from django.contrib.auth.models import User

from gatheros_subscription.directors import SubscriptionSurveyDirector
from gatheros_subscription.models import FormConfig, Lot
from importer.constants import KEY_MAP
from importer.forms import CSVSubscriptionForm
from importer.helpers import get_required_keys, get_survey_questions
from survey.models import Survey, Question


class LineData(object):
    """
        Essa classe é responsavel por preparar os dados em um iterável já
        mapeado os atributos já normalizados:
        
            - setar os nomes corretos das chaves do cabeçalho
            - fornecer informações de chaves invalidas

        Além de também realizar a persistencia através do método save.
    """

    def __init__(self, raw_data: OrderedDict) -> None:

        self.__raw_data = raw_data
        self.__invalid_keys = list()
        self.__internal_mapping = dict()
        self.__errors = dict()
        self._parse()

    def _parse(self):

        for raw_key, raw_value in self.__raw_data.items():

            parsed_key = raw_key.lower().strip()
            is_valid = False

            for key, value in KEY_MAP.items():
                if parsed_key in value['csv_keys'] or parsed_key == key:
                    is_valid = True
                    parsed_key = key
                    break

            if is_valid:
                self.__internal_mapping.update({parsed_key: raw_key})
                setattr(self, parsed_key, raw_value)
            else:
                self.__invalid_keys.append({
                    'key': self.normalize(raw_key),
                    'value': self.normalize(raw_value),
                })

    def get_errors(self):
        return self.__errors

    def get_survey_keys(self, survey: Survey=None):
        survey_keys = list()
        if survey:
            for item in self.__invalid_keys:
                if self.is_valid_survey_question(item['key'], survey):
                    survey_keys.append(item)

        return survey_keys

    def save(self,
             form_config: FormConfig,
             lot: Lot,
             user: User,
             survey: Survey = None,
             commit: bool = False):
        """

        Esse método faz a delegação da persistencia para um Form, passando pra
        ele os campos obrigatorios através de um objeto FormConfig.

        :param form_config: Object FormConfig
        :param survey: Object Survey
        :param lot: Object Lot
        :param user: Object User
        :param commit: Boolean
        :return: None
        """

        required_keys = get_required_keys(form_config=form_config)

        data = {'lot_id': lot.pk}

        for key, value in self:
            data.update({key: value})

        form = CSVSubscriptionForm(
            event=lot.event,
            user=user,
            required_keys=required_keys,
            data=data,
        )

        if survey:

            survey_data = self.fetch_survey_data(survey)
            survey_form = self.get_survey_form(
                survey=survey,
                data=survey_data,
            )

            if form.is_valid() and survey_form.is_valid():
                if commit:
                    subscription = form.save()
                    survey_form = self.get_survey_form(
                        survey,
                        survey_data,
                        subscription,
                    )
                    if not survey_form.is_valid():
                        raise Exception('Form que antes era valido agora não é')
                    survey_form.save()
                    subscription.author = survey_form.author
                    subscription.save()
            else:
                self.add_errors(form.errors)
                self.add_errors(survey_form.errors)

        elif form.is_valid():
            if commit:
                form.save()
        else:
            self.add_errors(form.errors)

    def __iter__(self):
        for i in self.__dict__.items():
            # Ignore mangled invalid keys
            if not i[0].startswith('_'):
                yield i

    def get_invalid_keys(self, survey: Survey = None):

        invalid_keys = list()

        for entry in self.__invalid_keys:

            key = entry['key'].lower().strip()

            if survey:

                if self.is_valid_survey_question(key, survey):
                    continue
                else:
                    invalid_keys.append(key)

            else:

                invalid_keys.append(key)

        return invalid_keys

    def get_raw_header_key(self, key: str):
        return self.__internal_mapping.get(key)

    def add_errors(self, errors):

        for fieldname, error_list in errors.items():

            if fieldname == '__all__':
                continue

            error = error_list[0]
            self.__errors.update({fieldname: error})

    def fetch_survey_data(self, survey):
        survey_data = {}

        questions = Question.objects.filter(survey=survey)
        for question in questions:
            survey_data.update({question.name: ''})

        for entry in self.__invalid_keys:

            key = entry['key']
            value = entry['value']

            valid_question = self.is_valid_survey_question(key, survey)

            if valid_question:
                survey_data.update({valid_question: value})

        return survey_data

    @staticmethod
    def get_survey_form(survey, data, subscription=None):
        survey_director = SubscriptionSurveyDirector(subscription)

        if subscription:
            return survey_director.get_form(
                survey=survey,
                data=data,
            )

        return survey_director.get_base_form(
            survey=survey,
            data=data,
        )

    @staticmethod
    def is_valid_survey_question(key: str, survey: Survey):

        all_questions = get_survey_questions(survey)
        key = key.lower().strip().replace('?', '')

        for question in all_questions:

            question_label = question.label.lower().strip().replace('?', '')

            if key == question_label:
                return question.name

        return False

    @staticmethod
    def normalize(string):
        return string.lower().strip().replace('?', '').replace(':', '')
