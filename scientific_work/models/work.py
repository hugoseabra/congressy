from django.db import models


class Work(models.Model):

    ARTICLE = 'artigo'
    BANNER = 'banner'
    SUMMARY = 'resumo'

    MODALITY_CHOICES = (
        (ARTICLE, 'Artigo'),
        (BANNER, 'Banner'),
        (SUMMARY, 'Resumo'),
    )

    ACADEMIC = 'ensino'
    MANAGEMENT = 'gestao'
    MARKETING = 'marketing'
    RESEARCH = 'pesquisa'

    AREA_CATEGORIES = (
        (ACADEMIC, 'Ensino'),
        (MANAGEMENT, 'Gestão'),
        (MARKETING, 'Marketing'),
        (RESEARCH, 'Pesquisa'),
    )

    modality = models.CharField(
        max_length=25,
        verbose_name="modalidades",
        choices=MODALITY_CHOICES,
        default=ARTICLE,
    )

    area_category = models.CharField(
        max_length=25,
        verbose_name="área temática",
        choices=AREA_CATEGORIES,
        default=ACADEMIC,
    )

    title = models.CharField(
        max_length=255,
        verbose_name="título",
    )

    summary = models.TextField(
        verbose_name="resumo",
        blank=True,
        null=True,
    )

    keywords = models.CharField(
        max_length=255,
        verbose_name="palavras chaves",
        help_text="Separados por vírgula",
    )

    article_file = models.FileField(
        upload_to='artigos/',
        blank=True,
        null=True
    )

    accepts_terms = models.BooleanField(
        verbose_name="termos de trabalhos científicos",
    )
