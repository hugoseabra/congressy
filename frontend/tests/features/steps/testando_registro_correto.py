from behave import then
from nose.tools import eq_
@then('Aparece a mensagem de registro bem sucedido contendo o \'{text}\'')
def step_impl(context,text):
    driver = context.browser
    assert driver.current_url.endswith('/login/?next=/manage/')
    mensagem_erro = driver.find_element_by_css_selector('.alert').text
    eq_(mensagem_erro, '×\nSua conta foi criada com sucesso! Enviamos um email para "'+text+'", click no link do email para ativar sua conta.')
1