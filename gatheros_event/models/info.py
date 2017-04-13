from django.db import models
from . import Event


class Info(models.Model):
    """ Informações de evento """

    text = models.TextField(verbose_name='texto')
    event = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True, verbose_name='evento')

    image1 = models.ImageField(verbose_name='imagem 1', null=True, blank=True)
    image2 = models.ImageField(verbose_name='imagem 2', null=True, blank=True)
    image3 = models.ImageField(verbose_name='imagem 3', null=True, blank=True)
    image4 = models.ImageField(verbose_name='imagem 4', null=True, blank=True)
    video = models.FileField(verbose_name='vídeo', null=True, blank=True)

    class Meta:
        verbose_name = 'Informação de Evento'
        verbose_name_plural = 'Infomações de Eventos'
        ordering = ['event']

    def __str__(self):
        return self.event.name
