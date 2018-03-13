# Survey - Formulário de Pesquisa

## Domínio

### Formulário (Survey)

- deve ter data de criação;
- deve ter descrição;


### Pergunta (Question)

- Percente a um formulário;
- Nome deve ser sempre único para o formulário, a não ser que que seja um 
pergunta de múltiplas escolhas;


### Opção de Pergunta (Option)

- Pertence a uma pergunta;
- Deve sempre ser de uma pergunta que suporte opções: SELECT, RADIO ou CHECKBOX;
- Deve ser possível definir uma opção como "intro" que define o primeiro 
pergunta em branco;
- Não pode haver mais de uma pergunta como "Intro" em uma pergunta;
- Não pode haver duas opções com mesmo valor para a mesma pergunta;


### Respostas (Answer)

- Percentece a uma pergunta;
- Pode ou não ser de um usuário _Django_;
- Se vinculado a um usuário _Django_, o usuário deve ter apenas uma resposta de
uma pergunta;
- Sempre deve existir um valor;
- O usuário deve visualizar o valor selecionado conforme exibido na tela;
- deve ter data de criação;
 
# Intenção

Obter uma estrutura única para todas as atividades de **Questionário**:

1. **Gerenciar de Questionário:** 
    1. Criar novo questionário;
    1. Resgatar questionário preexistente;
    1. Alterar questionário;
    1. Excluir questionário;    
1. **Gerenciar de perguntas:**
    1. Adicionar uma pergunta;
    1. Resgatar uma pergunta;
    1. Editar uma pergunta;
    1. Excluir uma pergunta;
1. **Opções de Pergunta:**
    1. Adicionar uma opção em pergunta;
    1. Resgatar opções de pergunta;
    1. Excluir uma opção de pergunta;
1. Renderizar formulário;
1. **Gerenciar de Respostas:**
    1. Receber dados de submissão e gerar respostas;
    1. Resgatar respostas;
    1. Alterar dados de submissão de um autor comum;
    1. Excluir dados 

## Gerenciamento de Questionário

### Criar
```python
# Service é responsável para abstrair toda complexidade.
service = SurveyService()
 
# Objeto de questionário com suporte a todas as ações
survey = service.create(
    name='Meu questionário',
    description='Formulário exemplo'
)
```

### Resgatar

```python
# Service é responsável para abstrair toda complexidade.
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
```


### Alterar

```python
# Service é responsável para abstrair toda complexidade.
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
survey.name = 'Meu questionário editado'
survey.description = 'Descrição editada'
survey.save()
```

### Excluir

```python
# Service é responsável para abstrair toda complexidade.
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
 
# Remove todo questionário com suas relações.
survey.delete()
```

## Gerenciamento de Perguntas

### Novo Pergunta

É possível crar uma Pergunta e depois adicionar ao Questionário:

```python
question_service = QuestionService()
 
question = question_service.create(
    type=constants.INPUT_TYPE,
    label='Qual o seu nome?',
    required=True,
    help_text='Informe o seu nome completo.'
)
 

survey.add_question(question)
```

Criar a pergunta diretamente pelo Questionário:

```python
question = survey.create_question(
    type=constants.INPUT_TYPE,
    label='Qual o seu nome?',
    required=True,
    help_text='Informe o seu nome completo.'
)
```

### Listar Perguntas

```python
questions = survey.get_questions()
print(questions)
```

Saída:

```python
{
    1: Question object,
    2: Question object,
    3: Question object,
    4: Question object,
    5: Question object,
    6: Question object,
    7: Question object,
    8: Question object,
}
```

### Recupera uma Pergunta

```python
# Pelo nome único
question = survey.get_question_by_name('qual-o-seu-nome-?')
 
# Pela label - deve ser exata
question = survey.get_question_by_name(question.slugify('Qual o seu nome?'))
 
# Pelo ID
question = survey.get_question(pk=1)
print(question)
```

Saída:

```python
Question object

```

### Alterar uma Pergunta

```python
# Pelo nome único
question = survey.get_question_by_name('qual-o-seu-nome-?')
 
# Pela label - deve ser exata
question = survey.get_question_by_name(question.slugify('Qual o seu nome?'))
 
# Pelo ID
question = survey.get_question_by_pk(1)
 
question.label = 'Qual o seu nome (editado)?'
question.save()
```


### Excluir uma Pergunta

O questinário não tem suporte a excluir uma pergunta. A exclusão deve ser feita
pelo próprio objeto da Pergunta:

```python
# Pela pergunta
question = survey.get_question_by_name('qual-o-seu-nome-?')
question.delete()
```

## Gerenciar opções de Pergunta


### Nova Opção na Pergunta
Questionário não possui suporte a gerenciar as opções. Isso deve ser feito
pelo próprio objeto da Pergunta. Não é possível criar opções isoladamente:


```python
question_service = QuestionService()
 
question = survey.create_question(
    type=constants.SELECT,
    label='Sexo',
)
 
# Adicionar opção.
question.add_option('Masculino')
```

### Listar opções

```python
question = survey.get_question_by_pk(1)
  
try:
    print(question.get_options())
 
except QuestionDoesSupportOptions as e:
    print(str(e))

```

Saída:

```python
{
    1: Option object,
    2: Option object,
}
```

### Resgatar Opção


```python
question = survey.get_question_by_pk(1)
 
# Recuperar pelo ID
option = question.get_option(1)
```


### Excluir Opção na Pergunta

```python
question = survey.get_question_by_pk(1)
 
# Remove pelo ID
question.remove_option_by_id(1)
 
# Pelo objeto de Option
question = survey.get_question_by_pk(1)
option = question.get_option(1)
option.delete()
```

## Renderização de Formulário

O formulário será renderizado a partir de um objeto de **Form** do _Django_:

```python
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
 
# Retorna um formulário vazio
survey.get_form()
 
# Retorna um formulário populado
author_service = AuthorService()
 
# Recupera author pelo ID
author = author_service.get(pk=1)
 
# Recupera author pelo USER (se houver)
author = author_service.get_by_user(user=user)
 
survey.get_form(author=author)
 
# Ou pode-se pegar o formulário diretamente de um user
survey.get_form(user=user)
```

## Recuperar Respostas

```python
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
 
# Todas as Respostas 
survey.get_answers()
 
# Respostas de um autor
# Retorna um formulário populado
author_service = AuthorService()
 
# Recupera author pelo ID
author = author_service.get(pk=1)
 
# Recupera author pelo USER (se houver)
author = author_service.get_by_user(user=user)
   
survey.get_answers(author)
 
# Ou pode-se pegar o formulário diretamente de um user
survey.get_answers(user=user)
```

# Salvar Novas Respostas de um Novo Autor

```python
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
  
# Formulário sem autor
form = survey.get_form(data=data, initial={})
 
try: 
    # Os dados serão salvos e um novo autor será gerado. 
    form.save()
 
except SurveySaveError as e: 
    print(str(e))
     
    # Form também já possui informações de validação 
    form.errors

```

# Alterar Respostas de um Autor

```python
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
 
# Retorna um formulário vazio
survey.get_form(author)
 
# Retorna um formulário populado
author_service = AuthorService()
 
# Recupera author pelo ID
author = author_service.get(pk=1)
 
# Recupera author pelo USER (se houver)
author = author_service.get_by_user(user)
 
# Formulário com autor
form = survey.get_form(author=author)
 
# Formulário com usuário
form = survey.get_form(user=user)
 
try: 
    # Os dados serão salvos e um novo autor será gerado. 
    form.save()
 
except SurveySaveError as e: 
    print(str(e))
     
    # Form também já possui informações de validação 
    form.errors

```
    
## Excluir dados de um Author

```python
service = SurveyService()
 
# Recupera questionario com ID=1
survey = service.get(pk=1)
 
# Retorna um formulário populado
author_service = AuthorService()
author = author_service.get(pk=1)
 
survey.delete_data(author)
 
# Ou pode-se pegar o formulário diretamente de um user
survey.delete_data(user=user)
```
