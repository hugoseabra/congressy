"""
Task to send e-mails
"""

from buzzlead import tasks
from buzzlead.celery import app


@app.task(bind=True,
          rate_limit='10/m',  # Processar até 10 tasks por minuto
          # default_retry_delay=30,  # retry in 30s
          ignore_result=True)
def confirm_bonus(self, token: str, email_campaign_owner: str, order_id: str):
    try:
        return tasks.confirm_bonus(token, email_campaign_owner, order_id)

    except Exception as exc:
        raise self.retry(exc=exc)
