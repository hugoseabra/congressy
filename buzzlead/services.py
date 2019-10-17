from . import tasks


def confirm_bonus(token: str, email_campaign_owner: str, order_id: str):

    return tasks.confirm_bonus(
        token=token,
        email_campaign_owner=email_campaign_owner,
        order_id=order_id,
    )
