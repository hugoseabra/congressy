Feature: Testando a tela de registro

  Scenario: Usuario tenta criar a conta mas coloca o sobrenome
    Given Usuario entra na pagina de registro
    When Preenche o campo nome com 'hugo '
    And Preenche o campo de email com 'hugoseabra19@gmail.com'
    And Clica em registrar
    Then Aparece a mensagem de erro para alertar de colocar o sobrenome

  @selecionado
  Scenario: Usuario tenta criar a conta mas coloca um email ja em uso
     Given Usuario entra na pagina de registro
     When Preenche o campo nome com 'Hugo Seabra '
     And Preenche o campo de email com 'diegotolentino@gmail.com'
     And Clica em registrar
     Then Aparece a mensagem de erro para alertar que o email esta em uso
     
  Scenario: Usuario tenta criar a conta mas não coloca @ no email
    Given Usuario entra na pagina de registro
    When Preenche o campo de email com 'hugoseabra19gmail.com>'
    And Preenche o campo nome com '<Hugo Seabra>'
    Then Aparece a mensagem que o email nao possui o @