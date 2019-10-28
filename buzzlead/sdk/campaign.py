from .base import CreateResource, BaseResource


class Campaign(BaseResource):
    endpoint = '/campaigns/validate/{codigo}?token={token}'

    def validate(self):
        return self.request(method='GET')
