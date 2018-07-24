KEY_MAP = {
    'name': {
        'verbose_name': 'Nome',
        'description': 'nome do participante',
        'csv_keys': ['nome', 'name', ],
        'possible_values': [],
    },
    'gender': {
        'verbose_name': 'Sexo',
        'description': 'sexo do participante',
        'csv_keys': ['sexo', 'genero', 'género'],
        'possible_values': [],
    },
    'email': {
        'verbose_name': 'Email',
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
        'verbose_name': 'Telefone',
        'description': 'telefone do participante',
        'csv_keys': ['phone', 'telephone', 'fone', 'telefone'],
        'possible_values': [],
    },
    'birth_date': {
        'verbose_name': 'Data de Nascimento',
        'description': 'data de nascimento no seguinte formato: dd/mm/aaaa',
        'csv_keys': ['data de nasc'],
        'possible_values': [],
    },
    'street': {
        'verbose_name': 'Rua',
        'description': 'Local de residencia do participante',
        'csv_keys': ['rua'],
        'possible_values': [],
    },
    'complement': {
        'verbose_name': 'Completo',
        'description': 'Complemento do endereço',
        'csv_keys': ['complemento'],
        'possible_values': [],
    },
    'number': {
        'verbose_name': 'Número',
        'description': 'Numero do endereço caso não tenha, informar S/N.',
        'csv_keys': ['numero', 'número'],
        'possible_values': [],
    },
    'village': {
        'verbose_name': 'Bairro',
        'description': 'Bairro',
        'csv_keys': ['bairro'],
        'possible_values': [],
    },
    'zip_code': {
        'verbose_name': 'CEP',
        'description': 'CEP',
        'csv_keys': ['cep'],
        'possible_values': [],
    },
    'city': {
        'verbose_name': 'Cidade',
        'description': 'cidade do participante',
        'csv_keys': ['cidade', 'municipio'],
        'possible_values': [],
    },
    'uf': {
        'verbose_name': 'Estado',
        'description': 'estado do participante',
        'csv_keys': ['uf', 'estado'],
        'possible_values': [],
    },
    'institution': {
        'verbose_name': 'Instituição',
        'description': 'Local onde o participante trabalha',
        'csv_keys': ['instituicao', 'instituição'],
        'possible_values': [],
    },
    'institution_cnpj': {
        'verbose_name': 'CNPJ da Instituição',
        'description': 'cnpj da instituição de trabalho',
        'csv_keys': ['cnpj', 'instituição_cnpj', 'instituicao_cnpj'],
        'possible_values': [],
    },
    'function': {
        'verbose_name': 'Ocupação',
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
