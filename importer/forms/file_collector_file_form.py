from django import forms

from attendance.models import AttendanceService


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if ext.lower() != '.txt':
        raise ValidationError(u'Extensão de arquivo não suportada.')


class FileCollectorFileForm(forms.Form):
    collector_file = forms.FileField(
        label="Arquivo",
        validators=[validate_file_extension],
    )

    CHOICES = [('checkin', 'Check-in'),
               ('checkout', 'Check-out')]

    type = forms.ChoiceField(
        label="Tipo de serviço",
        choices=CHOICES,
        widget=forms.RadioSelect,
    )

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['services'] = forms.ModelChoiceField(
            queryset=AttendanceService.objects.filter(event=event),
            label="Serviço de atendimento"
        )



