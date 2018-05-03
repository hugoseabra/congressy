from datetime import datetime

from django import forms

from core.util.date import DateTimeRange


def has_quantity_conflict(optional):
    num_subs = optional.num_consumed
    quantity = optional.quantity or 0

    if 0 < quantity <= num_subs:
        return True

    return False


def has_sub_end_date_conflict(optional):
    if optional.date_end_sub and datetime.now() > optional.date_end_sub:
        return True

    return False


def has_schedule_conflict(optional_service, subscription):
    new_start = optional_service.schedule_start
    new_end = optional_service.schedule_end

    is_restricted = optional_service.restrict_unique

    """
        TO BE CONTINUED FROM HERE
        
        FIND A WAY TO SCAN ALL OTHER SERVICES TO FIND CONFLICT
        
    """

    for sub_optional in optional_service.sub:

        start = sub_optional.optional.schedule_start
        stop = sub_optional.optional.schedule_end
        is_sub_restricted = \
            sub_optional.optional.restrict_unique

        session_range = DateTimeRange(start=start, stop=stop)
        has_conflict = (new_start in session_range or new_end in
                        session_range)

        if has_conflict is True and (is_restricted or is_sub_restricted):
            return True


    return False
