from .exceptions import CongressyAPIException


class Transporter(object):

    def __init__(self):
        import requests
        self.sess = requests.Session()

    def request(self,
                method,
                uri,
                headers=None,
                data=None,
                params=None,
                **kwargs):
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
                 api_header_key='Token',
                 transporter_class=Transporter):
        self.api_key = api_key
        self.api_header_key = api_header_key

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        self.base_url = base_url
        self.transporter = transporter_class()

    def get_uri(self, endpoint: str):
        if not endpoint.startswith('/'):
            endpoint = '/{}'.format(endpoint)

        return '{}{}'.format(self.base_url, endpoint)

    def request(self,
                method,
                endpoint,
                headers=None,
                data=None,
                params=None,
                **kwargs):

        default_headers = {
            'User-Agent': 'congressy-sdk-python/0.0.1',
            'Content-Type': 'application/json; charset=utf-8',
        }

        if self.api_key:
            authorization_value = '{} {}'.format(
                self.api_header_key,
                self.api_key
            )
            default_headers.update({
                'Authorization': authorization_value,
            })

        if not headers or isinstance(headers, dict) is False:
            headers = dict()

        headers.update(default_headers)

        return self.transporter.request(
            method,
            self.get_uri(endpoint),
            headers=headers,
            data=data,
            params=params,
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
