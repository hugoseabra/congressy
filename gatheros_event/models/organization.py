from django.db import models


# @TODO Estratégia de resgate de infos sociais da organização. Possível transferência de dados de membro em caso de interno ou get_<field>_display() para resgatar os dados.
# @TODO gerar slug único do nome
class Organization(models.Model):
    """ Organização """
    name = models.CharField(max_length=100, verbose_name='nome')
    description = models.TextField(null=True, blank=True, verbose_name='descrição')

    avatar_width = models.PositiveIntegerField(null=True, blank=True)
    avatar_height = models.PositiveIntegerField(null=True, blank=True)
    avatar = models.ImageField(blank=True, null=True, width_field='avatar_width', height_field='avatar_height',
                               verbose_name='foto')

    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)

    cash_provider = models.CharField(max_length=10, blank=True, null=True, verbose_name='provedor de recebimento')
    cash_data = models.CharField(max_length=10, blank=True, null=True, verbose_name='dados para recebimento')
    active = models.BooleanField(default=True, verbose_name='ativo')
    internal = models.BooleanField(default=True, verbose_name='gerado internamente')

    class Meta:
        verbose_name = 'organização'
        verbose_name_plural = 'organizações'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_members(self, group=None):
        if not group:
            return self.members.all()

        return self.members.filter(group=group)

    def is_member(self, person, group=None):
        for member in self.get_members(group=group):
            if member.person == person:
                return True

        return False

    def get_member_by_person(self, person, group=None):
        for member in self.get_members(group=group):
            if member.person == person:
                return member

        return None
