""" Formulários da mix_boleto """

from django import forms

from mix_boleto import models


class SyncResourceForm(forms.ModelForm):
    """ Formulário de mix_boleto.SyncResource """

    class Meta:
        fields = '__all__'
        model = models.SyncResource


class SyncCategoryForm(forms.ModelForm):
    """ Formulário de mix_boleto.SyncCategory """

    class Meta:
        fields = '__all__'
        model = models.SyncCategory


class MixBoletoForm(forms.ModelForm):
    """ Formulário de mix_boleto.MixBoleto """

    class Meta:
        fields = '__all__'
        model = models.MixBoleto


class SyncBoletoForm(forms.ModelForm):
    """ Formulário de mix_boleto.SyncBoleto """

    class Meta:
        fields = '__all__'
        model = models.SyncBoleto


class SyncSubscriptionForm(forms.ModelForm):
    """ Formulário de mix_boleto.SyncSubscription """

    class Meta:
        fields = '__all__'
        model = models.SyncSubscription
