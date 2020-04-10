from cgsy_video import tasks
from project.celery import app


@app.task(bind=True,
          queue='cgsy_video',
          options={'queue': 'cgsy_video'},
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=60,  # retry in 2m
          ignore_result=True)
def sync_event_user(self, event_pk):
    try:
        event_user = tasks.sync_event_user(event_pk)
        return 'User updated - data: {}'.format(event_user.to_dict())
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True,
          queue='cgsy_video',
          options={'queue': 'cgsy_video'},
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=60,  # retry in 2m
          ignore_result=True)
def sync_namespace(self, event_pk):
    try:
        namespace = tasks.sync_namespace(event_pk)
        return 'Namespace updated - data: {}'.format(namespace.to_dict())
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True,
          queue='cgsy_video',
          options={'queue': 'cgsy_video'},
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=60,  # retry in 2m
          ignore_result=True)
def sync_project(self, event_pk):
    try:
        project = tasks.sync_project(event_pk)
        return 'Project updated - data: {}'.format(project.to_dict())
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True,
          queue='cgsy_video',
          options={'queue': 'cgsy_video'},
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=60,  # retry in 2m
          ignore_result=True)
def create_video_config(self, event_pk):
    try:
        config = tasks.create_video_config(event_pk)
        return 'Video config created - event: {}'.format(config.event.name)
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True,
          queue='cgsy_video',
          options={'queue': 'cgsy_video'},
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=60,  # retry in 2m
          ignore_result=True)
def sync_subscriber(self, subscription_pk):
    try:
        subscriber = tasks.sync_subscriber(subscription_pk)
        if not subscriber:
            return 'Subscriber deleted - {}'.format(subscription_pk)

        return 'Subscriber updated - data: {}'.format(subscriber.to_dict())

    except Exception as exc:
        raise self.retry(exc=exc)
