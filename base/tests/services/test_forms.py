"""
    Testing forms base
"""

from django import forms
from django.db import models
from django_fake_model import models as f
from test_plus.test import TestCase

from base.forms import CombinedFormBase


class AnyModel(f.FakeModel):
    name1 = models.CharField(verbose_name='Test Form', max_length=10)
    age1 = models.PositiveIntegerField(verbose_name='age', max_length=3)


class Form1(forms.ModelForm):
    class Meta:
        model = AnyModel
        fields = '__all__'


class Form2(forms.Form):
    name2 = forms.CharField(label='Test Form')
    age2 = forms.IntegerField(label='age')


class MultiForm(CombinedFormBase):
    form_classes = (
        ('form1', Form1),
        ('form2', Form2),
    )


class CombinedFormConfigurationTest(TestCase):
    """
        Testa métodos privados de validação de CombinedForm.
    """

    def test_check_form_classes(self):
        """
            Testa configuração de "form_classes"
        """

        # Form configurado errado: form_classes não é tuple.
        class MultiForm(CombinedFormBase):
            form_classes = [Form1, Form2]

        with self.assertRaises(Exception) as e:
            MultiForm()

        msg = '"form_classes" deve ser configurado com um tuple de tuples'
        self.assertIn(msg, str(e.exception))

        # Form configurado errado: form_classes não é um tuple de tuples.
        class MultiForm(CombinedFormBase):
            form_classes = (Form1, Form2)

        with self.assertRaises(Exception) as e:
            MultiForm()

        msg = 'Cada item de "form_classes" deve ser um tuple de dois índices.'
        self.assertIn(msg, str(e.exception))

        # Form configurado errado: cada item de form_classes não possui dois
        # índices.
        class MultiForm(CombinedFormBase):
            form_classes = ((Form1,), (Form2,),)

        with self.assertRaises(Exception) as e:
            MultiForm()

        msg = 'Cada item de "form_classes" deve ser um tuple de dois índices.'
        self.assertIn(msg, str(e.exception))

    def test_check_instances_configuration(self):
        """
            Testa se instances esta de acordo com a configuração de
            "form_classes" em CombinedForm.
        """
        with self.assertRaises(Exception) as e:
            MultiForm(instance=AnyModel())

        msg = 'O parâmetro "instance" não é usada em "CombinedFormBase"'
        self.assertIn(msg, str(e.exception))

        # Instances passado sem ser dict()
        with self.assertRaises(Exception) as e:
            MultiForm(instances=AnyModel())

        msg = 'Instances must be a dict()'
        self.assertIn(msg, str(e.exception))

        # Instances com chaves diferente das configuradas em "form_classes"
        with self.assertRaises(Exception) as e:
            MultiForm(instances={
                'form1': AnyModel(),
                'form_nops': AnyModel(),
            })

        msg = 'Você deve informar um dict() cujas chaves sejam as mesmas' \
              ' utilizadas em "form_classes"'
        self.assertIn(msg, str(e.exception))

    def test_check_display_fields(self):
        """
            Testa exceção se algum campo informado em "display_fields" não
            consta na instância do formulário.
        """
        comb_form = MultiForm()
        form = comb_form.form_instances.get('form1')

        # Todos os fieds estão ok, eles existem.
        display_fields = ('name1', 'age1',)
        comb_form._check_display_fields(form, display_fields)

        # Campos que não existem no form
        display_fields = ('any1',)

        with self.assertRaises(Exception) as e:
            comb_form._check_display_fields(form, display_fields)

        msg = 'O formulário "{}" não possui o campo "{}"'.format(
            form.__class__,
            'any1'
        )
        self.assertIn(msg, str(e.exception))

    def test_configure_form_fields(self):
        """
            Testa se configuração de form suporta integração com
            "display_fields".
        """
        comb_form = MultiForm()
        form = comb_form.form_instances.get('form1')

        # Exibe somente um campo: name1
        display_fields = ('name1',)

        comb_form._configure_form_fields(form, display_fields)

        # age1 não consta em 'fields' do form.
        self.assertIn('name1', form.fields.keys())
        self.assertNotIn('age1', form.fields.keys())

        # Exibe somente um campo: age1
        display_fields = ('age1',)

        # Renovando form
        comb_form = MultiForm()
        form = comb_form.form_instances.get('form1')
        comb_form._configure_form_fields(form, display_fields)

        # name1 não consta em 'fields' do form.
        self.assertNotIn('name1', form.fields.keys())
        self.assertIn('age1', form.fields.keys())

    def test_create_form_instances(self):
        """
            Testa a criação de instâncias de forms
        """
        comb_form = MultiForm()
        self.assertIsInstance(comb_form.form_instances.get('form1'), Form1)
        self.assertIsInstance(comb_form.form_instances.get('form2'), Form2)


class CombinedFormPersistenceTest(TestCase):
    """
        Testes de persistência de CombinedForm
    """
    def test_save(self):
        """
            Testa se save() retorna um dict com todas instâncias dos models
            dos formulários configurados em "form_classes".  
        """
        name1 = 'name1'
        age1 = 10

        name2 = 'name2'
        age2 = 20

        comb_form = MultiForm(data={
            'name1': name1,
            'name2': name2,
            'age1': age1,
            'age2': age2,
        })
        self.assertTrue(comb_form.is_valid())
