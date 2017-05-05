from . import AbstractField


class DefaultField(AbstractField):
    class Meta:
        verbose_name = 'Campo Padrão'
        verbose_name_plural = 'Campos Padrão'
        ordering = ['order']

    def __str__( self ):
        return self.label
