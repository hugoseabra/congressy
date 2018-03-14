Feature: Testando tela de redefinicao de senha

  Scenario: Link de redefinicao expirou
    Given Usuario entra na pagina de redefinicao de senha pelo link 'https://test.congressy.com/reset-password/confirmation/MTE3/4tu-3b780ebab5d2ee0e2475/' 'expirado'
    When Usuario vizualiza a tela
    Then A pagina deve ter o titulo de painel 'REDEFINIÇÃO DE SENHA'
    And O texto 'Este link já foi utilizado, já expirou ou é de uma versão antiga do sistema.' em 'p.text-center:nth-child(1)'
    And O texto 'Por favor, solicite outro link para redefinir sua senha.' em 'p.text-center:nth-child(2)'
    And Um botao com texto 'Nova solicitação'

  Scenario: Link de redefinicao nao expirou
    Given Usuario entra na pagina de redefinicao de senha pelo link 'http://0.0.0.0:8001/reset-password/confirmation/Mg/4u1-435d18fa85e80acd7296/' 'não expirado'
    When Usuario vizualiza a tela
    Then A pagina deve ter o titulo de painel 'REDEFINIÇÃO DE SENHA'
    And O texto 'Por favor, informe sua nova senha duas vezes para que possamos verificar se você a digitou corretamente.' em '.text-center'
    And Um campo do tipo 'password' em '#id_new_password1'
    And Um campo do tipo 'password' em '#id_new_password2'

