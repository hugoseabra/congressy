from behave import given, when, then
import time
from nose.tools import eq_
from selenium import webdriver

@when('Preenche o campo de email com \'{text}\'')
def step_impl (context,text):
    driver = context.browser
    email = driver.find_element_by_id('email')
    email.send_keys(text)
    text_low = text.lower()
    eq_(email.get_attribute('value'), text_low)



@when('Preenche o campo de senha com \'{text}\'')
def step_impl (context,text):
    driver = context.browser
    senha = driver.find_element_by_id('password')
    senha.send_keys(text)

@when('Clica em entrar')
def step_impl (context):
    driver = context.browser
    login_button = driver.find_element_by_tag_name('button')
    login_button.click()
    time.sleep(1)

@then ('Ele entra na pagina de minhas inscricoes')
def step_impl (context):
    driver = context.browser
    assert driver.current_url.endswith('/manage/')
    h1 = driver.find_element_by_tag_name('h1').text
    eq_(h1, 'Minhas inscrições')
