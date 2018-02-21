Feature: Testando o Login

  Scenario: Usuario digita o email
    Given pagina de login
    When ele digitar o seu email no campo
    Then A tela de login deve aparecer o campo email preenchido com o "email"
