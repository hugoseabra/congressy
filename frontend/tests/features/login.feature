Feature: Testando o login

  Scenario: Usuario loga no sistema

    Given um usuario
    When Eu logo
    Then Eu vejo a pagina de minhas inscricoes
