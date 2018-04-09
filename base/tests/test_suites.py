from abc import abstractmethod
from test_plus.test import TestCase


class ManagerPersistenceTestCase(TestCase):
    """ Testes de persistência de dados de manager: criação e edição. """
    manager_class = None
    """
    :type: Manager
    Classe do Manager a ser testada.
    """

    data = None
    """
    :type: dict
    Dados a serem enviados para criação e edição:
    Criação:
        - ele usará exatamente o que for informad.
    Edição:
        - o valores dos campos obrigatórios serão mantidos (informados em
         "required_fields") e valores informados em "data_edit_to" serão
         alterados.
    """

    required_fieds = ()
    """
    :type: tuple
    Campos obrigatórios a serem mantidos na edição.
    """

    data_edit_to = {}
    """
    :type: dict
    Campos a serem alterados na edição.
    """

    def _create_manager(self, instance=None, data=None):
        if not data:
            data = self.data

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def _create_instance(self, manager=None):
        if not manager:
            manager = self._create_manager()

        valid = manager.is_valid()

        if not valid:
            self.fail(manager.errors)

        return manager.save()

    def create(self):
        """ Cria uma instância model ligado ao manager """
        manager = self._create_manager()
        instance = self._create_instance(manager)
        self.assertIsInstance(instance, manager.Meta.model)
        return instance

    def edit(self):
        """ Edita dados de um model ligado ao manager """
        instance = self._create_instance()

        data = {}
        for field_name in self.required_fieds:
            if field_name not in self.data:
                self.fail(
                    'O campo "{}" em "required_fields" não existe em'
                    ' "data".'.format(field_name)
                )
            data[field_name] = self.data.get(field_name)

        data.update(self.data_edit_to)

        manager = self._create_manager(instance=instance, data=data)

        valid = manager.is_valid()

        if not valid:
            self.fail(manager.errors)

        instance = manager.save()
        self.assertIsInstance(instance, manager.Meta.model)

        for field_name, value in self.data_edit_to.items():
            self.assertEqual(getattr(instance, field_name), value)

    @abstractmethod
    def test_create(self):
        """ Testa criação. """
        pass

    @abstractmethod
    def test_edit(self):
        """ Testa edição. """
        pass


class ApplicationServicePersistenceTestCase(TestCase):
    """ Testes de persistência de dados de application service: criação e
    edição.
    """
    application_service_class = None
    """
    :type: ApplicationService
    Classe do Application a ser testada.
    """

    data = None
    """
    :type: dict
    Dados a serem enviados para criação e edição:
    Criação:
        - ele usará exatamente o que for informad.
    Edição:
        - o valores dos campos obrigatórios serão mantidos (informados em
         "required_fields") e valores informados em "data_edit_to" serão
         alterados.
    """

    required_fieds = ()
    """
    :type: tuple
    Campos obrigatórios a serem mantidos na edição.
    """

    data_edit_to = {}
    """
    :type: dict
    Campos a serem alterados na edição.
    """

    def _create_service(self, instance=None, data=None):
        if not data:
            data = self.data

        if instance is not None:
            service = self.application_service_class(
                instance=instance,
                data=data
            )
        else:
            service = self.application_service_class(data=data)

        return service

    def _create_instance(self, service=None):
        if not service:
            service = self._create_service()

        valid = service.is_valid()

        if not valid:
            self.fail(service.errors)

        return service.save()

    def create(self):
        """ Cria uma instância model ligado ao manager """
        service = self._create_service()
        instance = self._create_instance(service)
        self.assertIsInstance(instance, service.manager_class.Meta.model)
        return instance

    def edit(self):
        """ Edita dados de um model ligado ao manager """
        instance = self._create_instance()

        data = {}
        for field_name in self.required_fieds:
            if field_name not in self.data:
                self.fail(
                    'O campo "{}" em "required_fields" não existe em'
                    ' "data".'.format(field_name)
                )
            data[field_name] = self.data.get(field_name)

        data.update(self.data_edit_to)

        service = self._create_service(instance=instance, data=data)

        valid = service.is_valid()

        if not valid:
            self.fail(service.errors)

        instance = service.save()
        self.assertIsInstance(instance, service.manager_class.Meta.model)

        for field_name, value in self.data_edit_to.items():
            self.assertEqual(getattr(instance, field_name), value)

    @abstractmethod
    def test_create(self):
        """ Testa criação. """
        pass

    @abstractmethod
    def test_edit(self):
        """ Testa edição. """
        pass



