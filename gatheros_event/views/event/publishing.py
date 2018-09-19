from django.contrib import messages
from django.http import HttpResponse

from gatheros_event.helpers.publishing import event_is_publishable
from gatheros_event.models import Member
from gatheros_event.views.mixins import EventViewMixin


class EventPublishView(EventViewMixin):
    http_method_names = ['post', ]

    def post(self, request,  *args, **kwargs):

        desired_state = request.POST.get('state')
        event = self.get_event()

        is_in_org = False
        person = self.request.user.person

        org_pk = event.organization_id
        try:
            Member.objects.get(organization_id=org_pk, person_id=person.pk)
            is_in_org = True
        except Member.DoesNotExist:
            pass

        if not is_in_org:
            return HttpResponse(status=401)

        is_publishable = event_is_publishable(event)
        published_msg = 'Evento publicado com sucesso!'
        unpublished_msg = 'Evento despublicado com sucesso!'
        unpublishable_msg = 'Evento não publicavel'

        erro_msg = 'Não foi possivel alterar o status de publicação do seu ' \
                   'evento'

        if desired_state == 'publish':

            if event.published:
                messages.success(request, published_msg)
                return HttpResponse(status=200)
            else:
                if is_publishable:
                    event.published = True
                    event.save()
                    messages.success(request, published_msg)
                    return HttpResponse(status=201)
                else:
                    messages.warning(request, unpublishable_msg)
                    return HttpResponse(unpublishable_msg, status=400)

        elif desired_state == 'unpublish':

            if not event.published:
                messages.success(request, unpublished_msg)
                return HttpResponse(status=200)

            else:
                event.published = False
                event.save()
                messages.success(request, unpublished_msg)
                return HttpResponse(status=201)

        messages.error(request, erro_msg)
        return HttpResponse("Estado desconhecido", status=500)
