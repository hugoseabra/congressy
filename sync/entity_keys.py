sync_file_keys = [
    'persons',
    'subscriptions',
    'transactions',
    'transaction_statuses',
    'attendance_services',
    'checkins',
    'checkouts',
]

person_required_keys = [
    'uuid',
    'name',
    'created',
    'modified',
]

person_other_keys = [
    'gender',
    'email',
    'city_id',
    'city_international',
    'zip_code',
    'zip_code_international',
    'street',
    'number',
    'complement',
    'village',
    'state_international',
    'address_international',
    'country',
    'ddi',
    'phone',
    'cpf',
    'international_doc_type',
    'international_doc',
    'birth_date',
    'rg',
    'orgao_expedidor',
    'synchronized',
    'term_version',
    'politics_version',
    'occupation',
    'pne',
    'institution',
    'institution_cnpj',
    'function',
    'website',
    'facebook',
    'twitter',
    'linkedin',
    'skype',
]

subscription_required_keys = [
    'uuid',
    'lot_id',
    'person_id',
    'origin',
    'code',
    'event_count',
    'created',
    'modified',
    'event_id',
]

subscription_other_keys = [
    # 'debts'
    # 'transactions' -> OK
    # 'payments'
    # 'subscription_products'
    # 'subscription_services'
    # 'works'
    # 'raffle_winners'
    # 'checkins',
    # 'installment_contracts'
    'status',
    'created_by',
    'attended',
    'count',
    'attended_on',
    'synchronized',
    'notified',
    'congressy_percent',
    'author',
    'completed',
    'test_subscription',
    'tag_info',
    'tag_group',
    'obs',
]

transaction_required_keys = [
    'uuid',
    'type',
    'subscription_id',
    'lot_id',
    'lot_price',
    'amount',
    'liquid_amount',
]

transaction_other_keys = [
    # 'payment',
    # 'statuses',  -> OK
    'status',
    'date_created',
    'part_id',
    'installments',
    'installment_part',
    'installment_amount',
    'boleto_url',
    'boleto_expiration_date',
    'credit_card_holder',
    'credit_card_first_digits',
    'credit_card_last_digits',
    'manual',
    'manual_payment_type',
    'manual_author',
    'data',
]

transaction_status_required_keys = [
    'id',
    'status',
    'date_created',
    'transaction',
    'data',
]

attendance_service_required_keys = [
    # 'checkins -> ok
    # 'lot_category_filters',
    'id',
    'name',
    'event',
    'created_on',
    'checkout_enabled',
    'with_certificate',
    'printing_queue_webhook',
    'printer_number',
    'pwa_pin',
    'accreditation',
]

checkin_required_keys = [
    # 'checkout, -> OK
    'id',
    'created_on',
    'created_by',
    'registration',
    'attendance_service_id',
    'subscription',
    'printed_on',
]

checkout_required_keys = [
    'id',
    'created_on',
    'created_by',
    'registration',
    'checkin_id',
]
