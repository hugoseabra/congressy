KEY_MAP = {
    'name': {
        'verbose_name': 'nome',
        'description': 'nome do participante',
        'csv_keys': ['nome'],
        'possible_values': [],
    },
    'email': {
        'verbose_name': 'email',
        'description': 'email do participante',
        'csv_keys': ['email', 'e-mail'],
        'possible_values': [],
    },
    'cpf': {
        'verbose_name': 'CPF',
        'description': 'documento CPF do participante',
        'csv_keys': ['cpf'],
        'possible_values': [],
    },
    'phone': {
        'verbose_name': 'telefone',
        'description': 'telefone do participante',
        'csv_keys': ['phone', 'telephone', 'fone', 'telefone'],
        'possible_values': [],
    },
    'birth_date': {
        'verbose_name': 'data de nascimento',
        'description': 'data de nascimento no seguinte formato: dd/mm/aaaa',
        'csv_keys': ['data de nasc'],
        'possible_values': [],
    },
    'address': {
        'verbose_name': 'endereço de residencia',
        'description': 'Local de residencia do participante',
        'csv_keys': ['endereço', 'endereco'],
        'possible_values': [],
    },
    'city': {
        'verbose_name': 'cidade',
        'description': 'cidade do participante',
        'csv_keys': ['cidade', 'municipio'],
        'possible_values': [],
    },
    'uf': {
        'verbose_name': 'estado',
        'description': 'estado do participante',
        'csv_keys': ['uf', 'estado'],
        'possible_values': [],
    },
    'institution': {
        'verbose_name': 'instituição de trabalho',
        'description': 'Local onde o participante trabalha',
        'csv_keys': ['instituicao', 'instituição'],
        'possible_values': [],
    },
    'institution_cnpj': {
        'verbose_name': 'cnpj da instituição de trabalho',
        'description': 'cnpj da instituição de trabalho',
        'csv_keys': ['cnpj', 'instituição_cnpj', 'instituicao_cnpj'],
        'possible_values': [],
    },
    'function': {
        'verbose_name': 'cargo',
        'description': 'cargo exercido do participante',
        'csv_keys': ['cargo', 'ocupação', 'ocupacao'],
        'possible_values': [],
    },

}

REQUIRED_KEYS = [
    'name',
    'email',
]
