#Todos os testes foram gerados usando o email: 'ana.carolina@me.com'

Feature: Testando hotsite
  Scenario: Usuario testa o evento 'Disponivel - Disponivel'
    Given Usuario logado na pagina eventos
    When Clica no evento '1'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And A mensagem de Inscrições encerradas
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner

     @select
  Scenario: Usuario testa o evento 'Futuro - Futuro'
    Given Usuario logado na pagina eventos
    When Clica no evento '2'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And 'Possui' o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o bloco do banner


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível e 1 Não-iniciado'
    Given Usuario logado na pagina eventos
    When Clica no evento '3'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o lote '1'
    And Existe o lote '2'

   Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Ilimitado'
    Given Usuario logado na pagina eventos
    When Clica no evento '4'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'


   Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Limitado (5 vagas)'
    Given Usuario logado na pagina eventos
    When Clica no evento '5'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Ilimitado'
    Given Usuario logado na pagina eventos
    When Clica no evento '6'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o lote '1'

#   Evento em que o usuario usado para teste está inscrito
  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica no evento '7'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Usuario ja esta logado aparece o botao de visualizar inscricao
    And Existe o lote '1'
    And Existe o lote '2'


  Scenario: 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Não-iniciado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica no evento '8'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o lote '1'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica no evento '9'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'
    And Existe o lote '2'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica no evento '10'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'
    And Existe o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Limitado Lotado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '11'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o lote '1'
    And Existe o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Não Disponível (data futura)'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '12'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 2 Lotes Expirados'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '13'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o lote '1'
    And Existe o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível e 1 Não-iniciado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '14'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Ilimitado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '15'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado (5 vagas)'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '16'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado Lotado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '17'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o lote '1'

#   Evento em que o usuario usado para teste está inscrito
  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '18'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Usuario ja esta logado aparece o botao de visualizar inscricao
    And Existe o lote '1'
    And Existe o lote '2'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Não-iniciado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '19'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o lote '1'


 Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica para ir para a pagina '2'
    And Clica no evento '20'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'
    And Existe o lote '2'