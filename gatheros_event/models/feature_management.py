from django.db import models

from .event import Event


class FeatureManagement(models.Model):
    """
    Recursos ativados pelo organizador.
    """
    class Meta:
        verbose_name = 'Gestão de Feature'
        verbose_name_plural = 'Gestão de Features'

    def __str__(self):
        return self.event.name

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field='uuid',
        verbose_name='evento',
        related_name='feature_management',
    )

    products = models.BooleanField(
        default=False,
        verbose_name='Opcionais',
        help_text="Você irá vender, opcionais como: hospedagem, alimentação, "
                  "camisetas?"
    )

    services = models.BooleanField(
        default=False,
        verbose_name='Atividades extras',
        help_text="Seu evento terá: workshops, minicursos?"
    )

    checkin = models.BooleanField(
        default=False,
        verbose_name='Checkin',
        help_text="Deseja realizar o checkin com nosso App gratuito?"
    )

    certificate = models.BooleanField(
        default=False,
        verbose_name='Certificado',
        help_text="Seu evento terá entrega de Certificados ?"
    )

    survey = models.BooleanField(
        default=False,
        verbose_name='Formulário Personalizado',
        help_text="Seu evento terá formulário com perguntas personalizadas ?"
    )

    raffle = models.BooleanField(
        default=False,
        verbose_name='Sorteios',
        help_text="Seu evento terá sorteios ?"
    )
