from django.utils import six
from django.utils.decorators import classonlymethod
from django.views import generic

from gatheros_subscription.views import SubscriptionViewMixin


class SubscriptionConfirmationView(SubscriptionViewMixin,
                                   generic.TemplateView):
    """ Inscrição de pessoa que já possui perfil. """
    subscription_user = None
    submitted_data = None
    template_name = 'subscription/subscription_confirmation.html'

    @classonlymethod
    def as_view(cls, user, submitted_data, **initkwargs):

        csrf = submitted_data.get('csrfmiddlewaretoken')
        if csrf:
            del submitted_data['csrfmiddlewaretoken']

        cleaned_submitted_data = {}
        for field_name, value in six.iteritems(dict(submitted_data)):
            if len(value) <= 1:
                cleaned_submitted_data[field_name] = value[0]
            else:
                cleaned_submitted_data[field_name] = value

        cls.subscription_user = user
        cls.submitted_data = cleaned_submitted_data

        return super(SubscriptionConfirmationView, cls).as_view(
            **initkwargs
        )

    def get_context_data(self, **kwargs):
        cxt = super(SubscriptionConfirmationView, self).get_context_data(
            **kwargs
        )
        cxt.update({
            'subscription_user': self.subscription_user,
            'submitted_data': self.submitted_data,
        })

        return cxt

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
