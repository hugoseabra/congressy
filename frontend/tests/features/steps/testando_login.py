from behave import given, when, then
import time
from nose.tools import eq_
from selenium import webdriver
@given ('um usuario')
def step_impl (context):
    context.browser.get('http://0.0.0.0:8001/login/')


@when('Eu logo')
def step_impl (context):
    driver = context.browser
    email = driver.find_element_by_id('email')
    email.send_keys('hugoseabra19@gmail.com')
    senha = driver.find_element_by_id('password')
    senha.send_keys('123')
    login_button = driver.find_element_by_tag_name('button')
    login_button.click()
    time.sleep(4)

@then ('Eu vejo a pagina de minhas inscricoes')
def step_impl (context):
    driver = context.browser
    #response = driver.getcode()
    #assert response.code == 200
    #assert driver.geturl().endswith('/manage/')
    h1 = driver.find_element_by_tag_name('h1').text
    eq_(h1, 'Minhas inscrições')
