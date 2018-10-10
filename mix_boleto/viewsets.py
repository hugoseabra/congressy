from django.http import HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view

from core.helpers import sentry_log
from gatheros_event.models import Event
from mix_boleto.mix import MixSync
from mix_boleto.models import SyncResource


@api_view(['POST'])
def synchronization_hook(request):
    data = request.data

    if not data:
        msg = 'Hook de sincronização entre MixEvents e Congressy com' \
              ' requisição sem dados.'

        sentry_log(message=msg, type='error', notify_admins=True)
        return HttpResponseBadRequest()

    event_id = data.get('event_id')
    resource_alias = data.get('resource_alias')

    if not event_id:
        msg = 'Hook de sincronização entre MixEvents e' \
              ' Congressy - event_id não encontrado.'

        sentry_log(message=msg, type='error', notify_admins=True)
        return HttpResponseBadRequest()

    if not resource_alias:
        msg = 'Hook de sincronização entre MixEvents e Congressy -' \
              ' resource_alias não encontrado.'

        sentry_log(message=msg, type='error', notify_admins=True)
        return HttpResponseBadRequest()

    event = Event.objects.get(pk=int(event_id))
    sync_resource = SyncResource.objects.get(alias=str(resource_alias))

    synchronizer = MixSync(
        resource_alias=sync_resource.alias,
        event_id=event.pk,
    )

    synchronizer.prepare()
    synchronizer.run()

    return Response(status=202)
