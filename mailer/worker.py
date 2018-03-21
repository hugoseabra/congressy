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
    'ignore_result': True, # ignora os resultados da task
}


@app.task(**task_params)
def send_mail(self, subject, body, to, attachment=None):
    try:
        return tasks.send_mail(subject, body, to, attachment)

    except SMTPAuthenticationError as exc:
        raise self.retry(exc=exc)


@app.task(**task_params)
def send_mass_mail(self, subject, body, to, attachment=None):
    try:
        return tasks.send_mass_mail(subject, body, to, attachment)

    except SMTPAuthenticationError as exc:
        raise self.retry(exc=exc)
