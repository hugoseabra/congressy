from django import forms


class NewWorkForm(forms.Form):
    modality = forms.ChoiceField(
        choices=[
            ('artigo', 'Artigo'),
            ('banner', 'Banner'),
            ('resumo', 'Resumo'),
        ],
        label='Modalidade'
    )

    area_category = forms.ChoiceField(
        choices=[
            ('ensino', 'Ensino'),
            ('gestao', 'Gestão'),
            ('marketing', 'Marketing'),
            ('pesquisa', 'Pesquisa'),
        ],
        label="Área temática",
    )

    title = forms.CharField(
        max_length=255,
        label="Título"
    )

    summary = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )

    keywords = forms.CharField(
        max_length=255,
        label="Palavras chave",
        help_text="Separados por vírgula"
    )

    author = forms.CharField(
        max_length=255,
        label="Autores",
        help_text="Separados por vírgula",
        widget=forms.HiddenInput(),
        required=False,
    )

    file = forms.FileField(label="Upload de artigos", required=False)

    accepts_terms = forms.BooleanField(
        initial=False,
        label="Declaro que li e estou de acordo com as regras para submissão "
              "de trabalhos científicos"
    )
