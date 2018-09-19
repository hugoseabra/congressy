from django import forms

from gatheros_event.models import FeatureConfiguration


class FeatureConfigurationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FeatureConfigurationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeatureConfiguration
        fields = '__all__'

    def save(self, commit=True):
        self.instance.last_updated_by = self.request.user.first_name + ' ' \
                                        + self.request.user.last_name
        if not self.instance.feature_multi_lots:
            self.instance.event.lots.all().update(
                active=False,
            )
            first = self.instance.event.lots.all().order_by('created').first()
            first.active = True
            first.save()

        return super().save(commit)
