from django.db import models

from . import Event

from .rules import info as rule


# @TODO redimensionar banner de topo para altura e largura corretas - 1920 x 900

class Info(models.Model):
    """ Informações de evento """

    CONFIG_TYPE_MAIN_IMAGE = 'image_main'
    CONFIG_TYPE_4_IMAGES = '4_images'
    CONFIG_TYPE_VIDEO = 'video'

    CONFIG_TYPE_CHOICES = (
        (CONFIG_TYPE_MAIN_IMAGE, 'Imagem única (Largura 360px, Altura: livre)'),
        (CONFIG_TYPE_4_IMAGES, '4 imagens pequenas (Tamanho: 300px x 300px)'),
        (CONFIG_TYPE_VIDEO, 'Vídeo (Youtube)'),
    )

    text = models.TextField(verbose_name='texto')
    event = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True, verbose_name='evento')

    config_type = models.CharField(max_length=15, null=True, blank=True, verbose_name='Exibição',
                                   choices=CONFIG_TYPE_CHOICES)
    image_main = models.ImageField(verbose_name='imagem principal', null=True, blank=True,
                                   help_text="Imagem única da descrição do evento (Largura: 360px).")
    image1 = models.ImageField(verbose_name='imagem pequena #1', null=True, blank=True,
                               help_text="Tamanho: 300px x 300px")
    image2 = models.ImageField(verbose_name='imagem pequena #2', null=True, blank=True,
                               help_text="Tamanho: 300px x 300px")
    image3 = models.ImageField(verbose_name='imagem pequena #3', null=True, blank=True,
                               help_text="Tamanho: 300px x 300px")
    image4 = models.ImageField(verbose_name='imagem pequena #4', null=True, blank=True,
                               help_text="Tamanho: 300px x 300px")
    youtube_video_id = models.TextField(verbose_name='ID do Youtube', null=True, blank=True,
                                        help_text="x: https://www.youtube.com/watch?v=xxxx")

    class Meta:
        verbose_name = 'Informação de Evento'
        verbose_name_plural = 'Infomações de Eventos'
        ordering = ['event']

    def __str__(self):
        return self.event.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Info, self).save(*args, **kwargs)

    def clean(self):
        rule.rule_1_imagem_unica_somente(self)
        rule.rule_2_4_imagens_somente(self)
        rule.rule_3_youtube_video_somente(self)
