from decimal import Decimal

from django.contrib.auth.models import User

from gatheros_event.event_specifications import payable
from gatheros_event.models import Organization, Event
from .mix_panel_event import MixPanelEvent
from .mix_panel_organization import MixPanelOrganization
from .mix_panel_user import MixPanelUser


def create_user(user: User):
    person = user.person

    return MixPanelUser(
        identity=str(person.pk),
        name=person.name,
        email=person.email or '',
        age=person.age or '',
        gender=person.get_gender_display() if person.gender else '',
        city_name=person.city.name if person.city_id else '',
        state_name=person.city.uf if person.city_id else '',
        country_name=person.country.upper() if person.country else '',
    )


def create_organization(org: Organization):
    return MixPanelOrganization(
        identity=org.pk,
        name=org.name,
        num_members=org.members.count(),
    )


def create_event(event: Event):
    city_name = ''
    state_name = ''

    if event.place and event.place.city_id:
        city_name = event.place.city.name
        state_name = event.place.city.uf

    event_payable = payable.EventPayable()

    transfer_tax = event.lots.filter(trasfer_tax=True).exists()

    percent = '{}%'.format(round(Decimal(event.congressy_percent), 2))

    return MixPanelEvent(
        identity=event.pk,
        name=event.name,
        city_name=city_name,
        state_name=state_name,
        paid=event_payable.is_satisfied_by(event),
        transfer_tax=transfer_tax,
        congressy_plan_percent=percent,
    )
