from .exceptions import CongressyAPIException


class Transporter(object):
    def __init__(self):
        import requests
        self.sess = requests.Session()

    def request(self, method, uri, headers, data=None, params=None, **kwargs):
        response = self.sess.request(method,
                                     uri,
                                     headers=headers,
                                     data=data,
                                     params=params,
                                     **kwargs)
        if response.status_code == 204:
            return True
        if not response.ok:
            raise CongressyAPIException(response)
        if 'results' in response.json():
            return response.json()['results']
        return response.json()


class Resource(object):

    def __init__(self,
                 base_url: str,
                 api_key: str = None,
                 transporter_class=Transporter):
        self.api_key = api_key

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        self.base_url = base_url
        self.transporter = transporter_class()

    def get_uri(self, endpoint: str):
        if not endpoint.startswith('/'):
            endpoint = '/{}'.format(endpoint)

        if not endpoint.endswith('/'):
            endpoint = '{}/'.format(endpoint)

        return '{}{}'.format(self.base_url, endpoint)

    def request(self, method, endpoint, **kwargs):
        headers = {
            'User-Agent': 'congressy-sdk-python/0.0.1',
            'Content-Type': 'application/json',
            'Authorization': self.api_key
        }
        return self.transporter.request(
            method,
            self.get_uri(endpoint),
            headers=headers,
            **kwargs,
        )

    def get(self, endpoint):
        raise NotImplementedError

    def list(self, endpoint):
        raise NotImplementedError

    def create(self, endpoint):
        raise NotImplementedError

    def update(self, endpoint):
        raise NotImplementedError

    def delete(self, endpoint):
        raise NotImplementedError
