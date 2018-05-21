from django.db import models
from gatheros_subscription.models import Subscription
import os
from .area_category import AreaCategory


class Work(models.Model):

    ARTICLE = 'artigo'
    BANNER = 'banner'
    SUMMARY = 'resumo'

    MODALITY_CHOICES = (
        (ARTICLE, 'Artigo'),
        (BANNER, 'Banner'),
        (SUMMARY, 'Resumo'),
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='trabalho',
        related_name='works',
    )

    modality = models.CharField(
        max_length=25,
        verbose_name="modalidades",
        choices=MODALITY_CHOICES,
        default=ARTICLE,
    )

    area_category = models.ForeignKey(
        AreaCategory,
        on_delete=models.DO_NOTHING,
        related_name="works",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="título",
    )

    summary = models.TextField(
        verbose_name="resumo",
    )

    keywords = models.CharField(
        max_length=255,
        verbose_name="palavras chaves",
        help_text="Separados por vírgula",
    )

    article_file = models.FileField(
        upload_to='scientific_work/artigos/',
        blank=True,
        null=True
    )

    banner_file = models.FileField(
        upload_to='scientific_work/banners/',
        blank=True,
        null=True
    )

    accepts_terms = models.BooleanField(
        verbose_name="termos de trabalhos científicos",
    )

    published = models.BooleanField(
        default=False,
        verbose_name="publicado",
    )

    @property
    def article_filename(self):
        return os.path.basename(self.article_file.name)


    @property
    def banner_filename(self):
        return os.path.basename(self.banner_file.name)