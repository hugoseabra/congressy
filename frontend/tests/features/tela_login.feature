Feature: Testando o login

  Scenario: Usuario entra na pagina de login
    Given Usuario entra na pagina de login
    When Usuario vizualiza a tela
    Then O campo '#email' deve ter o tipo 'email'
    And O campo '#password' deve ter o tipo 'password'

  Scenario: Usuario loga no sistema
    Given Usuario entra na pagina de login
    When Preenche o campo de email com 'HUGOSEABRA19@gmail.com'
    And Preenche o campo de senha com '123'
    And Clica em entrar
    Then Ele entra na pagina de minhas inscricoes

  Scenario: Usuario digita o email errado
    Given Usuario entra na pagina de login
    When Preenche o campo de email com 'hugoseabra19@gmail.com'
    And Preenche o campo de senha com '1234'
    And Clica em entrar
    Then Ele nao ira conseguir logar e ira aparecer a mensagem 'Por favor, entre com um usuário e senha corretos. Note que ambos os campos diferenciam maiúsculas e minúsculas.'
    Then Deve aparecer um captcha

  Scenario: Usuario clica em criar conta
    Given Usuario entra na pagina de login
    When Clica em criar conta
    Then Ele entra na pagina de registro

  Scenario: Usuario clica em esqueceu a senha
    Given Usuario entra na pagina de login
    When Clica em esqueceu senha
    Then Ele entra na pagina de resetar senha