from gatheros_event.models import Event
from gatheros_subscription.celery import app
from gatheros_subscription.helpers.export import export_event_data
from gatheros_subscription.helpers.subscription_async_exporter import \
    SubscriptionServiceAsyncExporter


@app.task(bind=True,
          rate_limit='5/m',  # Processaar até 5 tasks por minuto
          default_retry_delay=30,  # retry in 30s
          ignore_result=True)
def async_subscription_exporter_task(*args, **kwargs) -> None:
    event_pk = kwargs.get('event_pk')
    try:
        event = Event.objects.get(pk=event_pk)

        exporter = SubscriptionServiceAsyncExporter(event)

        if exporter.has_export_lock():
            raise Exception(
                'Exportação já está em andamento por outro usuário.'
            )

        exporter.create_export_lock()

        payload = export_event_data(event)
        if exporter.has_existing_export_files():
            exporter.remove_export_files()

        exporter.create_export_file(payload)

        exporter.remove_export_lock()
    except Exception as e:
        raise self.retry(exec=e)
