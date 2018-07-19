

KEY_MAP = {
    'name': {
        'description': 'nome do participante',
        'csv_keys': ['nome', 'name',],
        'possible_values': [],
    },
    'gender': {
        'description': 'sexo do participante',
        'csv_keys': ['sexo', 'genero', 'género'],
        'possible_values': [],
    },
    'email': {
        'description': 'email do participante',
        'csv_keys': ['email', 'e-mail'],
        'possible_values': [],
    },
    'cpf': {
        'description': 'documento CPF do participante',
        'csv_keys': ['cpf'],
        'possible_values': [],
    },
    'phone': {
        'description': 'telefone do participante',
        'csv_keys': ['phone', 'telephone', 'fone', 'telefone'],
        'possible_values': [],
    },
    'birth_date': {
        'description': 'data de nascimento no seguinte formato: dd/mm/aaaa',
        'csv_keys': ['data de nasc'],
        'possible_values': [],
    },
    'street': {
        'description': 'Local de residencia do participante',
        'csv_keys': ['rua'],
        'possible_values': [],
    },
    'complement': {
        'description': 'Complemento do endereço',
        'csv_keys': ['complemento'],
        'possible_values': [],
    },
    'number': {
        'description': 'Numero do endereço caso não tenha, informar S/N.',
        'csv_keys': ['numero', 'número'],
        'possible_values': [],
    },
    'village': {
        'description': 'Bairro',
        'csv_keys': ['bairro'],
        'possible_values': [],
    },
    'zip_code': {
        'description': 'CEP',
        'csv_keys': ['cep'],
        'possible_values': [],
    },
    'city': {
        'description': 'cidade do participante',
        'csv_keys': ['cidade', 'municipio'],
        'possible_values': [],
    },
    'uf': {
        'description': 'estado do participante',
        'csv_keys': ['uf', 'estado'],
        'possible_values': [],
    },
    'institution': {
        'description': 'Local onde o participante trabalha',
        'csv_keys': ['instituicao', 'instituição'],
        'possible_values': [],
    },
    'institution_cnpj': {
        'description': 'cnpj da instituição de trabalho',
        'csv_keys': ['cnpj', 'instituição_cnpj', 'instituicao_cnpj'],
        'possible_values': [],
    },
    'function': {
        'description': 'cargo exercido do participante',
        'csv_keys': ['cargo', 'ocupação', 'ocupacao'],
        'possible_values': [],
    },

}

REQUIRED_KEYS = [
    'name',
    'email',
    'gender',
]
