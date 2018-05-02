from datetime import datetime


def has_quantity_conflict(product):

    num_subs = product.num_consumed
    quantity = product.quantity or 0

    if 0 < quantity <= num_subs:
        return True

    return False


def has_quantity_conflict_with_future_prediction(product, is_in_storage=False):

    num_subs = product.num_consumed
    quantity = product.quantity or 0

    if is_in_storage:
        num_subs += 2

    if 0 < quantity <= num_subs:
        return True

    return False


def has_sub_end_date_conflict(product):

    if product.date_end_sub and datetime.now() > product.date_end_sub:
        return True

    return False
