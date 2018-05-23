Feature: Testando a tela de manage

  Scenario: Usuario entra na pagina manage
    Given Usuario entra na pagina de login
    When Usuario loga com  email 'hugoseabra19@gmail.com' e senha '123' e entra na pagina manage
    Then A pagina deve ter o logo
    And A pagina deve conter o campo do usuario no topo
    And A pagina deve conter o titulo Minhas Inscricoes

  #Scenario: Usuario entra na pagina manage clica no seu perfil
    #Given Usuario entra na pagina de login
    #When Usuario loga com  email 'hugoseabra19@gmail.com' e senha '123' e entra na pagina manage
    #And Clica no seu perfil
    #Then Deve descer um menu
    #And O menu deve ter meus dados
    #And O menu deve ter sair

