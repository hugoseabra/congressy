Feature: Testando a tela de recuperar senha

  Scenario: Usuario entra na pagina de recuperar senha
    Given Usuario entra na pagina de recuperar senha
    When Ele entra na pagina de resetar senha
    Then O campo '#email' deve ter o tipo 'email'

