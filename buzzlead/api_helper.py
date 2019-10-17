from datetime import date

from django.conf import settings

from buzzlead.sdk import Bonus, PreRegister


def create_bonus(token: str, email_campaign_owner: str, order_id: str):
    base_url = settings.BUZZLEAD_API_BASE_URL
    api_key = settings.BUZZLEAD_API_KEY

    context_data = {
        'email_user': email_campaign_owner,
        'order_id': order_id,
    }

    return Bonus(
        base_url=base_url,
        api_key=api_key,
        api_token=token,
        context_data=context_data,
    )


def create_preregister(event_date: date,
                       name: str, email: str,
                       event_name: str):
    base_url = settings.BUZZLEAD_API_BASE_URL
    api_key = settings.BUZZLEAD_API_KEY
    integrator_token = settings.BUZZLEAD_INTEGRATION_TOKEN

    context_data = {
        'service_integrator': 'hugo@congressy.com',
    }

    return PreRegister(
        base_url=base_url,
        api_key=api_key,
        api_token=integrator_token,
        context_data=context_data,
    )
