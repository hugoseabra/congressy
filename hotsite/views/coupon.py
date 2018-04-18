"""
    View usada para processar cupons.
"""

from django.http import Http404
from django.views import generic

from gatheros_subscription.models import Lot
from hotsite.views import EventMixin


class CouponView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/includes/form_lots_coupon.html'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        cxt = self.get_context_data(**kwargs)

        code = request.POST.get('coupon')
        if code:
            try:
                lot = Lot.objects.get(exhibition_code=str(code).upper())

                if lot.status != Lot.LOT_STATUS_RUNNING:
                    raise Http404

                cxt['lot'] = lot
                return self.render_to_response(cxt)

            except Lot.DoesNotExist:
                pass

        raise Http404
