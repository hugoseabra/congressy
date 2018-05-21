from django import forms

from core.forms.widgets import SplitDateTimeWidget
from scientific_work.models import WorkConfig


class WorkConfigForm(forms.ModelForm):

    event = None

    class Meta:
        model = WorkConfig
        fields = [
            'event',
            'date_start',
            'date_end',
            'presenting_type',
        ]

        widgets = {
            'date_start': SplitDateTimeWidget(),
            'date_end': SplitDateTimeWidget(),
            'event': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(WorkConfigForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    """
    Add this method to a custom form to use as an alternative
    to the save method.  When passed an object instance, the it
    will set values on the model corresponding to matching
    field names on the form.  

    Example:

    myobject = MyObject.objects.get(pk=1) 
    form = MyForm(request.POST) 
        if form.is_valid(): 
            form.update_instance(myobject)
    """

    def update_instance(self, instance, commit=True):
        for f in instance._meta.fields:
            if f.attname in self.fields:
                setattr(instance, f.attname, self.cleaned_data[f.attname])
        if commit:
            try:
                instance.save()
            except:
                return False
        return instance



