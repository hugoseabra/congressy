from django import forms


class NewWorkForm(forms.Form):

    modality = forms.ChoiceField(
        choices=[
            'Artigo',
            'Banner',
            'Resumo'
        ],
        label='Modalidade'
    )

    area_category = forms.ChoiceField(
        choices=[
            'Ensino',
            'Gestão',
            'Marketing',
            'Pesquisa',
        ],
        label="Área temática"
    )

    title = forms.CharField(
        max_length=255,
        label="Título"
    )

    summary = forms.CharField(
        widget=forms.Textarea,
    )

    keywords = forms.CharField(
        max_length=255,
        label="Palavras chave",
        help_text="Separados por vírgula"
    )

    author = forms.CharField(
        max_length=255,
        label="Autores",
        help_text="Separados por vírgula"
    )

    accepts_terms = forms.BooleanField(
        initial=False,
        label="Declaro que li e estou de acordo com as regras para submissão "
              "de trabalhos científicos"
    )


