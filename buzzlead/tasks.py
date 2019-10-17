from buzzlead.api_helper import create_bonus
from buzzlead.sdk.base.exceptions import BuzzLeadException


def confirm_bonus(token: str, email_campaign_owner: str, order_id: str):
    bonus = create_bonus(token=token,
                         email_campaign_owner=email_campaign_owner,
                         order_id=order_id)
    try:
        bonus.confirm()
    except BuzzLeadException:
        pass

