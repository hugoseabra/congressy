from . import worker


def confirm_bonus(token: str, email_campaign_owner: str, order_id: str):
    kwargs = {
        'token': token,
        'email_campaign_owner': email_campaign_owner,
        'order_id': order_id,
    }

    return worker.confirm_bonus.apply_async(kwargs=kwargs)
