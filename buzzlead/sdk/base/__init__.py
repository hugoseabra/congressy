from .http import Transporter


class BaseResource(object):
    endpoint = None

    def __init__(self,
                 base_url: str,
                 api_key: str,
                 api_token: str,
                 context_data: dict = None,
                 transporter_class=Transporter):

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        self.api_key = api_key
        self.api_token = api_token
        self.base_url = base_url
        self.context_data = context_data
        self.transporter = transporter_class()

    def get_uri(self):
        if not self.endpoint.startswith('/'):
            self.endpoint = '/{}'.format(self.endpoint)

        if not self.endpoint.endswith('/'):
            self.endpoint = '{}/'.format(self.endpoint)

        self.endpoint = self._translate_endpoint()

        return '{}{}'.format(self.base_url, self.endpoint)

    def request(self, method, **kwargs):
        headers = {
            'User-Agent': 'congressy-buzzlead-sdk-python/0.0.1',
            'Content-Type': 'application/json',
            'x-api-token-buzzlead': self.api_token,
            'x-api-key-buzzlead': self.api_key,
        }
        return self.transporter.request(
            method,
            uri=self.get_uri(),
            headers=headers,
            **kwargs
        )

    def _translate_endpoint(self):
        for key in self.context_data.keys():
            holder = '{' + key + '}'
            self.endpoint = self.endpoint.replace(holder,
                                                  self.context_data[key])

        return self.endpoint


class ListResource(BaseResource):
    def list(self):
        raise NotImplementedError


class RetrieveOneResource(BaseResource):
    def get(self):
        raise NotImplementedError


class CreateResource(BaseResource):
    def create(self, data: dict):
        raise NotImplementedError


class UpdateResource(BaseResource):
    def update(self, data: dict):
        raise NotImplementedError


class DeleteResource(BaseResource):
    def delete(self):
        raise NotImplementedError


class Resource(ListResource,
               RetrieveOneResource,
               CreateResource,
               UpdateResource,
               DeleteResource):
    pass
