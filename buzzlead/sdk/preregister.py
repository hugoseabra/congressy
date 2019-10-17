from .base import CreateResource


class PreRegister(CreateResource):
    endpoint = '/service/{service_integrator}/users/preregister'

    def create(self, data):
        return self.request(method='POST', data=data)
