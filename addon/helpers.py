def has_quantity_conflict(product):

    num_subs = product.num_consumed
    quantity = product.quantity or 0

    if 0 < quantity <= num_subs:
        return True

    return False
