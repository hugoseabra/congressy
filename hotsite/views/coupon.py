"""
    View usada para processar cupons.
"""

from django.http import Http404
from django.views import generic

from hotsite.views import EventMixin
from ticket.models import Ticket


class CouponView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/includes/form_ticket_coupon.json'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        cxt = self.get_context_data(**kwargs)

        code = request.POST.get('coupon')
        if code:
            try:

                ticket = Ticket.objects.get(
                    exhibition_code=str(code).upper(),
                    event_id=self.current_event.event.pk
                )

                if ticket.running is False:
                    raise Http404

                cxt['ticket'] = ticket
                return self.render_to_response(cxt)

            except Ticket.DoesNotExist:
                pass

        raise Http404
