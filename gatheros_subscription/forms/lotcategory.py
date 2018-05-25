""" Formulários de `Lot` """

from django import forms

from gatheros_subscription.models import LotCategory


class LotCategoryForm(forms.ModelForm):
    """ Formulário de categoria lote. """
    event = None

    class Meta:
        """ Meta """
        model = LotCategory
        fields = ('name',)

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.event = self.event
        return super().save(commit=commit)
