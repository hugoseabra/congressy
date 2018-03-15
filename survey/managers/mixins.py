"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django import forms


class Manager(forms.ModelForm):
    """
    Manager
    """

    def __init__(self, **kwargs):
        """
            TODO: Melhorar o comportamento deste:
                Caveat deste comportamento, quando alguém implementa este
                manager e criar uma assinatura diferente desta padrão como:
                '__init__(self, extra_field, **kwargs)'

                È então necessario dentro deste init dar um update no kwargs
                que será repassado a implementação base do manager(essa
                classe em si), da seguinte forma:

                'kwargs.update({'extra_required_field': extra_required_field})'

                Ao passar pelo construtor do manager, este kwarg ficará
                perdido, sendo necessario setar ele na mão como atributo do
                manager para poder acessa-lo depois, da seguinte forma:

                'self.extra_required_field = extra_required_field'

                Esse comportamento se torna necessario pois, esse atributo
                será usado para no metodo 'save' visto que esse atributo não
                está vinculado ao atributo 'self.instance'

        """

        self._check_argument_instances(kwargs)
        kwargs = self._clear_arguments(kwargs)
        super().__init__(**kwargs)

    def _check_argument_instances(self, arguments):
        """
        Verifica se os argumentos passados são relativos a algum campo
        relacional do model do Manager, verifica se o mesmo é um objeto
        da instância relacionada.
        """
        model_class = self.Meta.model
        ignored_keys = ('data',
                        'files',
                        'auto_id',
                        'prefix',
                        'initial',
                        'instance',
                        'error_class',
                        'label_suffix',
                        'empty_permitted',
                        'field_order',
                        'use_required_attribute',)

        related_classes = {}
        errors = {}

        # Varre todos os campos do model definidos em Meta procurando por
        # instancias relacionais que podem estar na lista de argumentos
        # 'arguments'
        for f in model_class._meta.get_fields():
            if f.is_relation and f.many_to_one:
                related_classes[f.name] = f.related_model

        # Percorre todos os argumentos contidos em kwargs que são enviados
        # via serviços a procura por algum campo relacional.
        for key, value in arguments.items():

            # Ignorando  as kwargs padrões.
            if key in ignored_keys:
                continue

            # Procurando por algum classe que seja uma das relacionais.
            if key in related_classes:
                related = related_classes.get(key)
                if not isinstance(value, related):
                    errors[key] = related

        if errors:
            msg = []
            for key, related_class in errors.items():
                msg_txt = '"{}" expects, "{}", received "{} {}" '
                msg.append(msg_txt.format(key,
                                          related_class,
                                          value,
                                          value.__class__))

            raise TypeError(
                'Argumentos não são instâncias de modelos relacionados:'
                ' {}'.format(', '.join(msg))
            )

    def _clear_arguments(self, kwargs):
        """ Limpa argumentos de campos relacionados a model do Manager. """
        model_class = self.Meta.model

        for f in model_class._meta.get_fields():
            if f.name in kwargs and f.is_relation and f.many_to_one:
                del kwargs[f.name]

        return kwargs
