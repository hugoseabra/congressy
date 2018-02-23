Feature: Testando a tela de registro


  Scenario: Usuario tenta criar a conta mas coloca o sobrenome
    Given Usuario entra na pagina de registro
    When Preenche o campo nome com 'hugo '
    And Preenche o campo de email com 'hugoseabra19@gmail.com'
    And Clica em registrar
    Then Aparece a mensagem de erro para alertar de colocar o sobrenome

  Scenario: Usuario tenta criar a conta mas coloca um email ja em uso
     Given Usuario entra na pagina de registro
     When Preenche o campo nome com 'Diego Tolentino'
     And Preenche o campo de email com 'diegotolentino@gmail.com'
     And Clica em registrar
     Then Aparece a mensagem de erro para alertar que o email esta em uso
     
  Scenario: Usuario tenta criar a conta mas não coloca @ no email
    Given Usuario entra na pagina de registro
    When Preenche o campo de email com 'hugoseabra19gmail.com'
    And Preenche o campo nome com 'Hugo Seabra'
    Then Aparece a mensagem que o email nao possui o @

  Scenario: Usuario consegue criar uma conta com sucesso
    Given Usuario entra na pagina de registro
    When Preenche o campo de email com 'teste@gmail.com'
    And Preenche o campo nome com 'João José'
    And Clica em registrar
    Then Aparece a mensagem de registro bem sucedido contendo o 'teste@gmail.com'

   @selecionado
  Scenario: Usuario clica em  Ja possui conta ? Entrar
    Given Usuario entra na pagina de registro
    When Clica em ja possui conta
    Then Usuario entra na pagina de login