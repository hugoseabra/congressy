
Feature: Testando hotsite

#  Scenario: Usuario testa o evento 'Disponivel - Disponivel'
#    Given Usuário entra no hotsite do evento '1'
#    Then Aparece o titulo
#    Then Aparece a data do evento
#    And A descricao rapida
#    And Aparece descricao do evento
#    And Existe o campo de descricao do organizador
#    And 'Não possui' o bloco de inscricao
#    And 'Não possui' o botao para fazer a inscricao
#    And 'Não possui' o campo email
#    And 'Não possui' o campo nome
#    And 'Não possui' o lote '1'
#    And 'Não possui' o lote '2'
#    And Existe o bloco do banner
#
#
#  Scenario: Usuario testa o evento 'Futuro - Futuro'
#    Given Usuário entra no hotsite do evento '2'
#    Then Aparece o titulo
#    Then Aparece a data do evento
#    And A descricao rapida
#    And Aparece descricao do evento
#    And Existe o campo de descricao do organizador
#    And 'Possui' o bloco de inscricao
#    And 'Possui' o botao para fazer a inscricao
#    And 'Não possui' o campo email
#    And 'Não possui' o campo nome
#    And 'Não possui' o lote '1'
#    And 'Não possui' o lote '2'
#    And Existe o bloco do banner


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível e 1 Não-iniciado'
    Given Usuário entra no hotsite do evento '3'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

   Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '4'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'


   Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '5'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Limitado Lotado'
    Given Usuário entra no hotsite do evento '6'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

#   Evento em que o usuario usado para teste está inscrito
  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '7'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'


  Scenario: 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Não-iniciado'
    Given Usuário entra no hotsite do evento '8'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '9'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And  O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '10'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And  O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

    @select
  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Expirado e 1 Disponível Limitado Lotado'
    Given Usuário entra no hotsite do evento '11'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 1 Lote Não Disponível (data futura)'
    Given Usuário entra no hotsite do evento '12'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' com Transferência de Taxas - 2 Lotes Expirados'
    Given Usuário entra no hotsite do evento '13'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível e 1 Não-iniciado'
    Given Usuário entra no hotsite do evento '14'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '15'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '16'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado Lotado'
      Given Usuário entra no hotsite do evento '17'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)'
   Given Usuário entra no hotsite do evento '18'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'


  Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Disponível Limitado Lotado e 1 Não-iniciado'
      Given Usuário entra no hotsite do evento '19'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'


 Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '20'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

 Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Expirado e 1 Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '21'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

 Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Expirado e 1 Disponível Limitado Lotado'
    Given Usuário entra no hotsite do evento '22'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

 Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 1 Lote Não Disponível (data futura)'
    Given Usuário entra no hotsite do evento '23'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o lote '1'
    And 'Não possui' o lote '2'

   Scenario: Usuario testa o evento 'Futuro e Pago c/ 'Lotes' sem Transferência de Taxas - 2 Lotes Expirados'
    Given Usuário entra no hotsite do evento '24'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

Scenario: Usuario testa o evento 'Futuro Publicado Insc. Desativadas - Futuro Publicado Insc. Desativadas'
    Given Usuário entra no hotsite do evento '25'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o lote '1'
    And 'Não possui' o lote '2'


# Scenario: Usuario testa o evento 'futuro-publicado-insc-simples-futuro-publicado-insc-simples/'
#    Given Usuário entra no hotsite do evento '26'
#    Then Aparece o titulo
#    Then Aparece a data do evento
#    And A descricao rapida
#    And Aparece descricao do evento
#    And Existe o campo de descricao do organizador
#    And Existe o bloco do banner
#    And 'Possui' o campo email
#    And 'Possui' o campo nome
#    And  O campo email tem o tipo email
#    And O campo nome tem o tipo text
#    And 'Possui' o bloco de inscricao
#    And 'Possui' o botao para fazer a inscricao
#    And 'Não possui' o lote '1'
#    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Disponível e 1 Não-iniciado'
    Given Usuário entra no hotsite do evento '27'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '28'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '29'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Disponível Limitado Lotado'
    Given Usuário entra no hotsite do evento '30'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '31'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'


  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Disponível Limitado Lotado e 1 Não-iniciado'
    Given Usuário entra no hotsite do evento '32'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '33'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Expirado e 1 Disponível Ilimitado'
    Given Usuário entra no hotsite do evento '33'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Expirado e 1 Disponível Limitado (5 vagas)'
    Given Usuário entra no hotsite do evento '34'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Possui' o campo email
    And 'Possui' o campo nome
    And  O campo email tem o tipo email
    And O campo nome tem o tipo text
    And 'Possui' o bloco de inscricao
    And 'Possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Expirado e 1 Disponível Limitado Lotado'
    Given Usuário entra no hotsite do evento '35'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 1 Lote Não Disponível (data futura)'
    Given Usuário entra no hotsite do evento '36'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Não possui' o lote '1'
    And 'Não possui' o lote '2'

  Scenario: Usuario testa o evento 'Futuro, Publicado e Gratuito c/ 'Lotes' - 2 Lotes Expirados'
    Given Usuário entra no hotsite do evento '37'
    Then Aparece o titulo
    Then Aparece a data do evento
    And A descricao rapida
    And Aparece descricao do evento
    And Existe o campo de descricao do organizador
    And Existe o bloco do banner
    And 'Não possui' o campo email
    And 'Não possui' o campo nome
    And 'Não possui' o bloco de inscricao
    And 'Não possui' o botao para fazer a inscricao
    And 'Possui' o lote '1'
    And 'Possui' o lote '2'