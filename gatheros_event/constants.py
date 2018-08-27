FREE_EVENT_FEATURES = {
    # Before event
    'feature_survey': True,
    'feature_certificate': True,
    'feature_products': True,
    'feature_services': True,
    'feature_internal_subscription': True,
    'feature_boleto_expiration_on_lot_expiration': False,
    'feature_multi_lots': False,
    'feature_import_via_csv': False,
    # During Event
    'feature_manual_payments': False,
    'feature_checkin': True,
}

PAID_EVENT_FEATURES = {
    # Before event
    'feature_survey': True,
    'feature_certificate': True,
    'feature_products': True,
    'feature_services': True,
    'feature_internal_subscription': True,
    'feature_boleto_expiration_on_lot_expiration': False,
    'feature_multi_lots': True,
    'feature_import_via_csv': False,
    # During Event
    'feature_manual_payments': False,
    'feature_checkin': True,
}