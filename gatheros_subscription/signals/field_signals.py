from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from gatheros_subscription.models import Field, Form


# Ref: http://schinckel.net/2012/02/06/pre-validating-many-to-many-fields./
@receiver(m2m_changed, sender=Field.forms.through)
def restrict_form_for_field(**kwargs):
    """
    Restringe campo a ser cadastro em formulários organização a qual pertence.

    Esta validação é feita em Signal por ser um ManyToMany. O Signal é
    disparado pelo Field e não pelo Model.

    Signal pode ser disparado tanto por Form quanto por Field, pois a relação
    é de visibilidade Bi-lateral. Como a relação está em Field, se o gatilho
    vier de form, o parâmetro `reverse` será True
    """

    action = kwargs.get('action')
    instance = kwargs.get('instance')

    # Ignora se todo o processo já foi verificado.
    if action == 'post_add' or action == 'post_clear':
        return

    def check_organization(form_instance, field_instance):
        """
        Verifca se formulário a ser vinculado é da mesma organização do campo.
        """
        event = form_instance.event
        if event.organization.pk != field_instance.organization.pk:
            raise ValidationError(
                'O formulário `{form_name} (#{form_pk})` não é da mesma'
                ' organização do campo `{field_name}`:'
                ' `{form_org_name} (#{form_org_pk})`. A organização do campo é'
                ' `{field_org_name} (#{field_org_pk})`'.format(
                    form_name=form_instance.event.name,
                    form_pk=form_instance.pk,
                    field_name=field_instance.name,
                    form_org_name=event.organization.name,
                    form_org_pk=event.organization.pk,
                    field_org_name=field_instance.organization.name,
                    field_org_pk=field_instance.organization.pk
                )
            )

    if isinstance(instance, Form):
        for field in Field.objects.filter(pk__in=kwargs.get('pk_set')):
            check_organization(instance, field)

    elif isinstance(instance, Field):
        for form in Form.objects.filter(pk__in=kwargs.get('pk_set')):
            check_organization(form, instance)

