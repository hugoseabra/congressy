"""
Task to send e-mails
"""
from smtplib import SMTPAuthenticationError

from mailer import tasks
from mailer.celery import app

task_params = {
    'bind': True,
    'rate_limit': '300/h',  # Tentar até 300x por hora
    'default_retry_delay': 15 * 60  # retry in 15m
}


@app.task(**task_params)
def send_mail(self, subject, body, to):
    try:
        return tasks.send_mail(subject, body, tasks
                               )
    except SMTPAuthenticationError as exc:
        raise self.retry(exc=exc)


@app.task(**task_params)
def send_mass_mail(self, subject, body, to):
    try:
        return tasks.send_mass_mail(subject, body, to)

    except SMTPAuthenticationError as exc:
        raise self.retry(exc=exc)
