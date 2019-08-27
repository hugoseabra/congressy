from django.db import models
from unidecode import unidecode


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    name_ascii = models.CharField(max_length=255)
    uf = models.CharField(max_length=2)

    def __unicode__(self):
        return '{}-{}'.format(self.name, self.uf)

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        self.name_ascii = unidecode(self.name)
        return super(City, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name_ascii']

