from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from gatheros_event.views.mixins import AccountMixin
from payment.forms import PagarMeCheckoutForm


class CheckoutView(AccountMixin, FormView):
    form_class = PagarMeCheckoutForm
    template_name = 'payments/checkout.html'
    success_url = reverse_lazy('public:payment-checkout')
    object = None

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.items())
        return initial

    def get_success_url(self):
        url = self.success_url
        querystrings = []
        for key, value in self.request.GET.items():
            if key == 'csrmiddlewaretoken':
                continue
            querystrings.append('{}={}'.format(key, value))

        return '{}?{}'.format(url, '&'.join(querystrings))

    def post(self, request, *args, **kwargs):
        next_url = self.request.POST.get('next_url')
        if next_url:
            self.success_url = next_url

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        non_field_errors = form.non_field_errors()
        for error in non_field_errors:
            messages.error(self.request, str(error))

        for hidden_field in form.hidden_fields():
            if hidden_field.errors:
                for error in hidden_field.errors:
                    messages.error(self.request, str(error))

        return super().form_valid(form)
