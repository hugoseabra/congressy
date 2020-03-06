"""
Task to send e-mails
"""

from mailer import tasks
from project.celery import app


@app.task(bind=True,
          queue='mailer',
          options={'queue': 'mailer'},
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          default_retry_delay=2 * 60,  # retry in 2m
          ignore_result=True)
def send_mail(self, subject, body, to, reply_to=None,
              attachment_file_path=None, ):
    try:
        return tasks.send_mail(
            subject=subject,
            body=body,
            to=to,
            reply_to=reply_to,
            attachment_file_path=attachment_file_path,
        )

    except Exception as exc:
        raise self.retry(exc=exc)
