# A sequeência deve parmanecer conforme regras de relacionamentos entre
# entidades
sync_file_keys = [
    'gatheros_subscription.lotcategory',
    'gatheros_subscription.lot',

    'gatheros_subscription.eventsurvey',
    'survey.survey',
    'survey.question',
    'survey.option',

    'addon.product',
    'addon.service',

    'auth.user',
    'gatheros_event.person',
    'gatheros_subscription.subscription',

    'survey.author',
    'survey.answer',
    
    'addon.subscriptionproduct',
    'addon.subscriptionservice',
    
    'payment.transaction',
    'payment.transactionstatus',

    'attendance.attendanceservice',
    'attendance.checkin',
    'attendance.checkout',
]

sync_schema_keys = [
    'process_type',
    'pk',
    'fields',
    'model',
    'process_time',
]
