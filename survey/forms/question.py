""" Forms used to manipulate the Question domain """
from django import forms


class QuestionCreateForm(forms.Form):
    """ Form used to create new questions """
    title = forms.CharField(help_text='O título da sua pergunta',
                            widget=forms.TextInput, required=True)
    is_required = forms.BooleanField(help_text='È obrigatório? ',
                                     required=True)




