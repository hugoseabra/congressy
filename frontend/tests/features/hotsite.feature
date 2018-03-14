Feature: Testando hotsite
  Scenario: Usuario testa o evento 'Disponivel - Disponivel'
    Given Usuario logado na pagina eventos
    When Clica no evento '1'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida 'existe'
    And A mensagem de Inscrições encerradas
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner

  Scenario: Usuario testa o evento 'Futuro - Futuro'
    Given Usuario logado na pagina eventos
    When Clica no evento '2'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida 'não existe'
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o bloco do banner


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível e 1 Não-iniciado'
    Given Usuario logado na pagina eventos
    When Clica no evento '3'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida 'não existe'
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
    And A descricao rapida 'não existe'
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
    And A descricao rapida 'não existe'
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
    And A descricao rapida 'não existe'
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o lote '1'

    @select
  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)'
    Given Usuario logado na pagina eventos
    When Rola a pagina ate o fim
    And Clica no evento '7'
    And Usuario vai para pagina de editar o evento e clica para visualizar pagina
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida 'não existe'
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And Existe o bloco de inscricao
    And Existe o botao para fazer a inscricao
    And Existe o lote '1'
    And Existe o lote '2'