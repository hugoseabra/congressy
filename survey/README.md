# Survey - Formulário de Pesquisa

## Domínio

### Formulário (Survey)

- deve ter data de criação;
- deve ter descrição;


### Pergunta (Question)

- Percente a um formulário;
- Nome deve ser sempre único para o formulário, a não ser que que seja um 
campo de múltiplas escolhas;


### Opção de Campo (Option)

- Pertence a uma pergunta;
- Deve sempre ser de um campo que suporte opções: SELECT, RADIO ou CHECKBOX;
- Deve ser possível definir uma opção como "intro" que define o primeiro 
campo em branco;
- Não pode haver mais de um campo como "Intro" em uma pergunta;
- Não pode haver duas opções com mesmo valor para a mesma pergunta;


### Respostas (Answer)

- Percentece a uma pergunta;
- Pode ou não ser de um usuário _Django_;
- Se vinculado a um usuário _Django_, o usuário deve ter apenas uma resposta de
uma pergunta;
- Sempre deve existir um valor;
- O usuário deve visualizar o valor selecionado conforme exibido na tela;
- deve ter data de criação;
 
