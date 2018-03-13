"""
    Formulario responsavel pela manipulação de objetos do tipo Survey a
    nivel de dominio, ou seja aplicando apenas as regras de dominio.
"""

from django import forms
from survey.models import Survey


class SurveyModelForm(forms.ModelForm):
    """
        Implementação do formulario.
    """

    class Meta:
        """ Meta """
        model = Survey
        fields = '__all__'
