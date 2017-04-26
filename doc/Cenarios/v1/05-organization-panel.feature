Feature: Gerenciamento de Organização

  Scenario: Visualiza painel da organização
    - Geral: Visualização idêntica ao do cenário "Perfil do usuário::Visualiza área restrita do organizador"
    - Informações da organzação: avatar e nome
    - Informação de quantidade de eventos vinculados e um botão "visualizar"
    - Lista de membros (nome, tipo, data de entrada), com filtro (tipo) e possibilidade de "adicionar", "editar" e
    "excluir"
    - Lista de convites pendentes (nome, e-mail, tipo, data de envio), com filtro (tipo) e possibilidade de "adicionar", "editar" e
    "excluir"

  Scenario: Novo convite
    Criar novo convite de acordo como tipo (admin ou auxiliar) e enviar.


  Scenario: Excluir convite
    Um convite, uma vez excluído, não permitirá que a pessoa previamente convidada entre na organização.


  Scenario: Editar convite
    Se exição for de mudança de tipo, o convite será reenviado para convidado.


  Scenario: Editar membro
    Só poderá ser editado o tipo e mudança será notificada para o membro.


  Scenario: Excluir membro
    Exclusão será notificada para o membro.
