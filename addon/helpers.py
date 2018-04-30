def has_quantity_conflict(product):

    num_subs = product.products.count()
    quantity = product.quantity or 0
    if 0 < quantity <= num_subs:
        return True

    return False
