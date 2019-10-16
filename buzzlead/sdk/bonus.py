from .base import CreateResource


class Bonus(CreateResource):
    endpoint = '/service/{email_user}/bonus/{order_id}/{status}'

    def create(self, data):
        return self.request(method='POST', data=data)
