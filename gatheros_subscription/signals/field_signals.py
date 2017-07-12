from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from gatheros_subscription.models import Field, Form


# Ref: http://schinckel.net/2012/02/06/pre-validating-many-to-many-fields./
@receiver(m2m_changed, sender=Field.forms.through)
def restrict_form_for_field(**kwargs):
    """
    Restringe campo a ser vinculado a formulários de organização a qual
    pertence.

    Esta validação é feita em Signal por ser um ManyToMany. O Signal é
    disparado pelo Field e não pelo Model.

    Signal pode ser disparado tanto por Form quanto por Field, pois a relação
    é de visibilidade Bi-lateral. Como a relação está em Field, se o gatilho
    vier de form, o parâmetro `reverse` será True
    """

    action = kwargs.get('action')
    instance = kwargs.get('instance')

    if action == 'pre_add':
        _pre_add_process_restriction(instance, kwargs.get('pk_set'))

    if action == 'post_remove':
        _post_remove_form_update(instance, kwargs.get('pk_set'))


def _pre_add_process_restriction(instance, pk_set):
    """
    Processa verificação de restrição de relação entre Field e Form
    :param instance: Instância de Field ou Form (reverse)
    :param pk_set:
        IDs da relação. Se normal, ID de Field, se reverso, ID de Form
    :type pk_set: list
    :raise: ValidationError
    """

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
        # Reverso, pk_set são de `Field`
        for field in Field.objects.filter(pk__in=pk_set):
            check_organization(instance, field)

    elif isinstance(instance, Field):
        # Normal, pk_set são de `Form`
        for form in Form.objects.filter(pk__in=pk_set):
            check_organization(form, instance)


def _post_remove_form_update(instance, pk_set):
    """
    Atualiza configurações de formulário com relação às referências do campo
    que acaba de ser removido. Os campos a serem atualizados são:
    - inactive_fields
    - required_configuration
    - order
    :param instance: Instância de Field ou Form (reverse)
    :param pk_set:
        IDs da relação. Se normal, ID de Field, se reverso, ID de Form
    :type pk_set: list
    """
    form_instances = []
    excluded_field_names = []

    if isinstance(instance, Form):
        # Reverso, pk_set são de `Field`
        fields = Field.objects.filter(pk__in=pk_set)
        excluded_field_names = [f.name for f in fields]
        form_instances.append(instance)

    elif isinstance(instance, Field):
        # Normal, pk_set são de `Form`
        excluded_field_names = [instance.name]
        form_instances = Form.objects.filter(pk__in=pk_set)

    else:
        return

    def update_order_list(form):
        """
        Atualiza lista de ordem de campos removendo os `Fields` que foram
        removidos da relação.
        """
        order_list = form.get_order_list()
        if not order_list:
            return

        updated_list = []
        for field_name in order_list:
            if field_name in excluded_field_names:
                continue

            updated_list.append(field_name)

        form.set_order_list(updated_list)

    def update_inactive_field_list(form):
        """
        Atualiza lista de campos inativos removendo os `Fields` que foram
        removidos da relação.
        """
        inactive_list = form.get_inactive_field_list()
        if not inactive_list:
            return

        updated_list = []
        for field_name in inactive_list:
            if field_name in excluded_field_names:
                continue

            updated_list.append(field_name)

        form.set_inactive_fields_list(updated_list)

    def update_required_configuration(form):
        """ Atualiza a configuração de campos obrigatórios do formulário. """
        config = form.required_configuration
        if not config:
            return

        for field_name in excluded_field_names:
            item = config.get(field_name)
            if item:
                del config[field_name]

        form.required_configuration = config

    for form_instance in form_instances:
        update_order_list(form_instance)
        update_inactive_field_list(form_instance)
        update_required_configuration(form_instance)
        form_instance.save()


@receiver(post_save, sender=Field)
def update_form_configurations(instance, **kwargs):
    """
    Atualiza configurações de formulário que possuem referência o nome do
    campo. São elas:
    - inactive_fields
    - required_configuration
    - order
    """
    # Disable when loaded by fixtures
    if kwargs.get('raw') is True:
        return

    if not instance.has_changed('name'):
        return

    forms = instance.forms.all()
    if not forms:
        return

    old_name = instance.old_value('name')
    name = instance.name

    def _update_fields_list(fields_list):
        """ Resgata lista e substitui valor antigo pelo novo. """
        updated_list = []
        for field_name in fields_list:
            if field_name == old_name:
                updated_list.append(name)
                continue

            updated_list.append(field_name)

        return updated_list

    def update_order(form):
        """ Atualiza referência em `order`. """
        order_list = form.get_order_list()
        if not order_list:
            return

        updated_list = _update_fields_list(order_list)
        form.set_order_list(updated_list)

    def update_inactive_fields(form):
        """ Atualiza referência em campos inativos. """
        inactive_list = form.get_inactive_fields_list()
        if not inactive_list:
            return

        updated_list = _update_fields_list(inactive_list)
        form.set_inactive_fields_list(updated_list)

    def update_required_configuration(form):
        """ Atualiza configuração de campos obrigatórios do formulário. """
        config = form.required_configuration
        item = config.get(old_name) if config else None
        if not item:
            return

        config[name] = item is True
        del config[old_name]

        form.required_configuration = config

    for related_form in forms:
        update_order(related_form)
        update_inactive_fields(related_form)
        update_required_configuration(related_form)
        related_form.save()
