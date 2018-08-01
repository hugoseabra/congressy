from django import forms

from core.forms.widgets import (
    AjaxChoiceField,
)


class CSVCityForm(forms.Form):
    """ Formulário de Person. """

    states = (
        ('', '----'),
            # replace the value '----' with whatever you want, it won't matter
        ("AC", "AC"),
        ("AL", "AL"),
        ("AP", "AP"),
        ("AM", "AM"),
        ("BA", "BA"),
        ("CE", "CE"),
        ("DF", "DF"),
        ("ES", "ES"),
        ("GO", "GO"),
        ("MA", "MA"),
        ("MT", "MT"),
        ("MS", "MS"),
        ("MG", "MG"),
        ("PA", "PA"),
        ("PB", "PB"),
        ("PR", "PR"),
        ("PE", "PE"),
        ("PI", "PI"),
        ("RJ", "RJ"),
        ("RN", "RN"),
        ("RS", "RS"),
        ("RO", "RO"),
        ("RR", "RR"),
        ("SC", "SC"),
        ("SP", "SP"),
        ("SE", "SE"),
        ("TO", "TO"),
    )
    empty = (
        ('', '----'),
    )

    state = forms.ChoiceField(label='Estado', choices=states)
    city = forms.IntegerField(widget=forms.HiddenInput)
    city_name = AjaxChoiceField(label='Cidade', choices=empty)
