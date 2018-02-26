from behave import when, then
import time
from nose.tools import eq_

@when('Preenche o campo nome com \'{text}\'')
def step_impl (context,text):
    driver = context.browser
    nome = driver.find_element_by_id('name')
    nome.send_keys(text)

@when('Clica em registrar')
def step_impl (context):
    driver = context.browser
    login_button = driver.find_element_by_css_selector('#submitButton')
    login_button.click()
    time.sleep(1)

@then ('Aparece a mensagem de erro para alertar de colocar o sobrenome')
def step_impl(context):
    driver = context.browser
    mensagem_erro = driver.find_element_by_css_selector('.alert').text
    eq_(mensagem_erro, '×\nVocê deve informar seu sobrenome para criar sua conta.')

@then ('Aparece a mensagem de erro para alertar que o email esta em uso')
def step_impl(context):
    driver = context.browser
    mensagem_erro = driver.find_element_by_css_selector('.alert').text
    eq_(mensagem_erro,'Esse email já existe em nosso sistema. Tente novamente.')

@then('Nao aceita o cadastro pois o input tem o tipo email')
def step_impl(context):
    driver = context.browser
    campo_email = driver.find_element_by_css_selector('#email').get_attribute('type')
    eq_(campo_email,'email')
