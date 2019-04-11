"""
Task to send e-mails
"""
from smtplib import SMTPAuthenticationError

from mailer import tasks
from mailer.celery import app

task_params = {
    'bind': True,
    'rate_limit': '10/m',  # Tentar até 10 tasks por minuto
    'default_retry_delay': 15 * 60,  # retry in 15m
    'ignore_result': True,  # ignora os resultados da task
}


@app.task(**task_params)
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

    except SMTPAuthenticationError as exc:
        raise self.retry(exc=exc)
