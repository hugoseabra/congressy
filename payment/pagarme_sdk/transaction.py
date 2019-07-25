from pagarme.resources import handler_request

from payment.pagarme_sdk.resources.routes import transaction_routes


def get_split_rules(transaction_id):
    return handler_request.get(
        transaction_routes.GET_TRANSACTION_SPLIT_RULES.format(transaction_id)
    )


def get_split_rule(transaction_id, split_rule_id):
    return handler_request.get(
        transaction_routes.GET_SPECIFIC_SPLIT_RULE.format(transaction_id,
                                                          split_rule_id)
    )
