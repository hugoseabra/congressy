from .base import BaseResource


class Bonus(BaseResource):
    endpoint = '/service/{email_user}/bonus/status/{order_id}/{status}'

    def confirm(self):
        self.context_data['status'] = 'confirmado'
        return self.request(method='POST')
