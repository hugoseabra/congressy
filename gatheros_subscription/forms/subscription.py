import json
from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import safestring, six
from kanu_locations.models import City

from gatheros_event.models import Person
from gatheros_subscription.models import Answer, Field, Lot, Subscription
from .event_form import EventConfigForm


class SubscriptionForm(EventConfigForm):
    """ Formulário de pré-inscrição. """
    def __init__(self, instance=None, hide_lot=True, *args, **kwargs):
        self.instance = instance

        super(SubscriptionForm, self).__init__(*args, **kwargs)

        self._adjust_initial_data()

        self._add_user_field()
        self._add_lot_field(hide_lot)

    def clean_lot(self):
        """ Limpa campo 'lot' """
        lot_pk = self.cleaned_data.get('lot')
        if not lot_pk:
            self.add_error('lot', 'Nenhum lote foi informado.')

        return Lot.objects.get(pk=lot_pk)

    def clean_name(self):
        """ Limpa campo 'name' """
        name = self.cleaned_data.get('name')
        name = name.strip()
        split = name.split(' ')
        if len(split) < 2:
            self.add_error('name', 'Informe nome e sobrenome.')

        return name

    def clean(self):

        force_string = [
            Field.FIELD_INPUT_DATETIME,
            Field.FIELD_INPUT_DATE,
        ]

        for f_name, gatheros_field in six.iteritems(self.gatheros_fields):
            value = self.cleaned_data.get(f_name)

            if gatheros_field.field_type == Field.FIELD_BOOLEAN:
                required = False

            else:
                required = gatheros_field.required

            if gatheros_field.field_type in force_string:
                value = str(value)

            if isinstance(value, str):
                value = safestring.mark_safe(value.strip())

            if value == '':
                value = None

            if not value and required:
                self.add_error(f_name, 'Você deve preencher este campo')

            if value:
                self.cleaned_data[f_name] = value

        return super(SubscriptionForm, self).clean()

    def save(self):
        """ Salva dados. """

        try:
            subscription = self._save_or_create_subscription()

        except Exception as e:
            raise e

        else:
            self._save_or_create_answers()
            return subscription

    def _adjust_initial_data(self):
        """ Ajusta valores iniciais de acordo com os campos."""

        if not self.instance:
            return

        try:
            self.initial.update({'user': self.instance.person.user.pk})

        except (ObjectDoesNotExist, AttributeError):
            pass

        for field_name, gatheros_field in six.iteritems(self.gatheros_fields):
            answer = gatheros_field.answer(subscription=self.instance)
            if not answer:
                continue

            if isinstance(answer, City):
                answer = answer.pk

            elif isinstance(answer, Answer):
                try:
                    answer = json.loads(answer.value)

                except ValueError:
                    continue

                if isinstance(answer, dict):
                    answer = answer['value']

            elif isinstance(answer, str):
                answer = answer.strip()

            self.initial.update({field_name: answer})

    def _save_or_create_subscription(self):
        """ Salva inscrição existente ou cria uma nova caso não exista. """
        lot = self.cleaned_data.get('lot')

        if self.instance:
            instance = self.instance
            instance.modified = datetime.now()

        else:
            instance = Subscription(
                origin=Subscription.DEVICE_ORIGIN_WEB,
                created_by=1,
            )

        self.instance = instance
        self.instance.person = self._save_or_create_person()
        self.instance.lot = lot
        self.instance.save()

        return self.instance

    def _save_or_create_person(self):
        """ Salva uma pessoa existente ou cria uma nova caso não exista. """
        try:
            if not self.instance:
                if not self.cleaned_data.get('user'):
                    raise User.DoesNotExist()

                user = User.objects.get(pk=self.cleaned_data['user'])
                person = user.person

            else:
                person = self.instance.person

        except ObjectDoesNotExist:
            # Para esta condição, os campos obrigatórios já deve estar contidos
            # nos campos padrão da plataforma.
            person = Person()

        for f_name, gatheros_field in six.iteritems(self.gatheros_fields):
            value = self.cleaned_data.get(f_name)

            if not hasattr(person, f_name):
                continue

            if f_name == 'city':
                value = City.objects.get(pk=value)

            setattr(person, f_name, value)

        person.save()

        return person

    def _save_or_create_answers(self):
        """ Salva respostas. """

        if not self.instance:
            raise Exception('A instância de inscrição deve estar setada.')

        # Campos
        for f_name, gatheros_field in six.iteritems(self.gatheros_fields):
            # Resgata responsta preexistente
            gatheros_answer = gatheros_field.answer(subscription=self.instance)

            # Se a resposta vir de Person ou outro objeto, ignorar
            if not isinstance(gatheros_answer, Answer):
                continue

            value = self.cleaned_data.get(f_name)

            if gatheros_field.field_type == Field.FIELD_BOOLEAN:
                output = 'Sim' if value is True else 'Não'
            else:
                output = None

            if value and gatheros_field.with_options:
                value, output = self._process_option_answers(
                    options=gatheros_field.options.all(),
                    output=output,
                    value=value,
                    is_multiple=gatheros_field.field_type in [
                        Field.FIELD_CHECKBOX_GROUP
                    ]
                )

            if value:
                value = {'value': value}

                if output:
                    value.update({'output': output})

                value = json.dumps(value)

            elif gatheros_field.field_type == Field.FIELD_BOOLEAN:
                value = json.dumps({'value': value, 'output': "Não"})

            # Se há resposta anterior e não há valor, exclui
            if gatheros_answer and not value:
                gatheros_answer.delete()
                continue

            # Se há valor e não há resposta anterior, criar
            if value and not gatheros_answer:
                gatheros_answer = Answer(
                    subscription=self.instance,
                    field=gatheros_field,
                )

            gatheros_answer.value = value
            gatheros_answer.save()

    # noinspection PyMethodMayBeStatic
    def _process_option_answers(
            self,
            options,
            output,
            value,
            is_multiple=False):
        """
        Processa resposta de opções de campo.

        :param options: Opções do campo
        :param output: Saída de leitura humana
        :param value: valor a ser gravado
        :param is_multiple: se seleção é múltipla
        :return: tuple
        """

        is_list = isinstance(value, list)

        selected = []
        selected_output = []

        for opt in options:
            # Se não for lista, verifica se é igual
            is_equal = not is_list and opt.value == value

            # Se for lista, verifica se seleção única e se valor consta
            is_selected = is_list and opt.value in value
            is_one_selection = is_selected and not is_multiple

            # Seja não-lista ou lista com seleção única
            if is_equal or is_one_selection:
                value = opt.value
                output = opt.name

                break

            # Se for lista com múltiplos valores e valor consta
            if is_multiple and opt.value in value:
                selected.append(opt.value)
                selected_output.append(opt.name)

        value = selected if selected else value
        output = selected_output if selected_output else output

        return value, output

    def _add_user_field(self):
        """ Adicionando campo `user` do tipo `hidden` no fromulário. """
        self.fields['user'] = forms.CharField(
            required=False,
            widget=forms.HiddenInput,
        )

    def _add_lot_field(self, hide_lot=True):
        """
        Adiciona o campo `lot` no formulário.
        """

        choices = [('', '- Selecione -')]
        lots = self.form.event.lots.all().order_by('name')
        [choices.append((lot.pk, lot.name,)) for lot in lots]

        lot = forms.ChoiceField(
            label='Lote',
            required=True,
            choices=choices,
            initial=self.instance.lot.pk if self.instance else None
        )

        event = self.form.event

        # Event com inscrição que não seja por lote deve esconder o campo
        if event.subscription_type != event.SUBSCRIPTION_BY_LOTS or hide_lot:
            lot.widget = forms.HiddenInput()

        self.fields['lot'] = lot


class SubscriptionAttendanceForm(forms.Form):
    """ Formulário de credenciamento de Inscrições. """
    def __init__(self, instance=None, *args, **kwargs):
        self.instance = instance
        super(SubscriptionAttendanceForm, self).__init__(*args, **kwargs)

    def attended(self, attended):
        """ Persiste atendimento de acordo com parâmetro. """
        self.instance.attended_on = datetime.now() if attended else None
        self.instance.attended = attended
        self.instance.save()
