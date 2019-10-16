from .exceptions import BuzzLeadAPIException


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
            raise BuzzLeadAPIException(response)
        if 'results' in response.json():
            return response.json()['results']
        return response.json()
