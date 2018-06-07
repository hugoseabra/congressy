from addon.models import Service
from core.util.date import DateTimeRange


def is_in_time_frame(first_optional: Service, second_optional:Service) \
        -> bool:
    is_first_restricted = first_optional.restrict_unique
    is_second_restricted = second_optional.restrict_unique

    if is_first_restricted or is_second_restricted:

        start_one = first_optional.schedule_start
        stop_one = first_optional.schedule_end

        start_two = second_optional.schedule_start
        stop_two = second_optional.schedule_end

        session_range_one = DateTimeRange(start=start_one, stop=stop_one)
        session_range_two = DateTimeRange(start=start_two, stop=stop_two)

        if start_one == start_two:
            return False

        if start_one in session_range_two:
            return False

        if start_two in session_range_one:
            return False

    return True


def get_all_options(all_optionals: list,
                    pre_existing_optionals: list, available_only: bool) \
        -> list:
    results = []
    for optional in all_optionals:

        available = not optional.has_quantity_conflict and \
                    not optional.has_sub_end_date_conflict

        if available:
            services = pre_existing_optionals
            for service in services:
                # Checks for bi-lateral time restrictions.
                if not is_in_time_frame(service.optional, optional):
                    available = False

        if available_only:
            results.append(optional)
        else:
            results.append({"optional": optional, "available": available})

    if not available_only:
        print('')
    return results
