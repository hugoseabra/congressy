Feature: Testando a tela de registro

  Scenario: Usuario entra na pagina de registro
    Given Usuario entra na pagina de registro
    When Usuario vizualiza a tela
    Then O campo '#email' deve ter o tipo 'email'
    And O campo '#name' deve ter o tipo 'text'


  Scenario: Usuario tenta criar a conta mas coloca o sobrenome
    Given Usuario entra na pagina de registro
    When Preenche o campo nome com 'hugo'
    And Preenche o campo de email com 'teste123@gmail.com'
    And Clica em registrar
    Then Aparece a mensagem de erro para alertar de colocar o sobrenome
    #And Deve aparecer um captcha

  Scenario: Usuario tenta criar a conta mas coloca um email ja em uso
     Given Usuario entra na pagina de registro
     When Preenche o campo nome com 'Hugo Seabra'
     And Preenche o campo de email com 'hugoseabra19@gmail.com'
     And Clica em registrar
     Then Aparece a mensagem de erro para alertar que o email esta em uso
     #And Deve aparecer um captcha

  Scenario: Usuario tenta criar a conta mas não coloca @ no email, testando input = email
    Given Usuario entra na pagina de registro
    When Preenche o campo de email com 'hugoseabra19gmail.com'
    And Preenche o campo nome com 'Hugo Seabra'
    And Clica em registrar
    Then Nao aceita o cadastro pois o input tem o tipo email

  Scenario: Usuario consegue criar uma conta com sucesso
    Given Usuario entra na pagina de registro
    When Preenche o campo de email com 'teste3@gmail.com'
    And Preenche o campo nome com 'João José'
    And Clica em registrar
    Then Aparece a mensagem de registro bem sucedido contendo o 'teste3@gmail.com'

  Scenario: Usuario clica em  Ja possui conta ? Entrar
    Given Usuario entra na pagina de registro
    When Clica em ja possui conta
    Then Usuario entra na pagina de login