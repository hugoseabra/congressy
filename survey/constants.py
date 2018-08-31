FIELD_INPUT_TEXT = 'input-text'
FIELD_INPUT_NUMBER = 'input-number'
FIELD_INPUT_DATE = 'input-date'
FIELD_INPUT_DATETIME = 'input-datetime-local'
FIELD_INPUT_EMAIL = 'input-email'
FIELD_INPUT_FILE_PDF = 'input-file-pdf'
FIELD_INPUT_FILE_IMAGE = 'input-file-image'
FIELD_INPUT_PHONE = 'input-phone'
FIELD_TEXTAREA = 'textarea'
FIELD_BOOLEAN = 'boolean'
FIELD_SELECT = 'select'
FIELD_CHECKBOX_GROUP = 'checkbox-group'
FIELD_RADIO_GROUP = 'radio-group'

PREDEFIENED_CPF = 'input-phone-cpf'
PREDEFIENED_CNPJ = 'input-phone-cnpj'
PREDEFIENED_PHONE = 'input-phone-phone'
PREDEFIENED_CELLPHONE = 'input-phone-cellphone'

TYPE_LIST = [
    'input-text',
    'input-number',
    'input-date',
    'input-datetime-local',
    'input-email',
    'input-phone',
    'input-phone-cpf',
    'input-phone-cnpj',
    'input-phone-phone',
    'input-phone-cellphone',
    'input-file-pdf',
    'input-file-image',
    'textarea',
    'boolean',
    'select',
    'checkbox-group',
    'radio-group',
]

TYPES = (
    (FIELD_INPUT_TEXT, 'Texto (255 caracteres)'),
    (FIELD_INPUT_NUMBER, 'Número'),
    (FIELD_INPUT_DATE, 'Data'),
    (FIELD_INPUT_DATETIME, 'Data e hora'),
    (FIELD_INPUT_EMAIL, 'E-mail'),
    (FIELD_INPUT_FILE_PDF, 'Envio de PDF'),
    (FIELD_INPUT_FILE_IMAGE, 'Envio de Imagem'),
    (FIELD_INPUT_PHONE, 'Telefone'),
    (FIELD_TEXTAREA, 'Texto longo'),
    (FIELD_BOOLEAN, 'SIM/NÃO'),
    (FIELD_SELECT, 'Lista simples'),
    (FIELD_CHECKBOX_GROUP, 'Múltipla escolha'),
    (FIELD_RADIO_GROUP, 'Escolha única'),
    (PREDEFIENED_CPF, 'CPF'),
    (PREDEFIENED_CNPJ, 'CNPJ'),
    (PREDEFIENED_PHONE, 'Número de Telefone Fixo'),
    (PREDEFIENED_CELLPHONE, 'Número de Celular'),
)
