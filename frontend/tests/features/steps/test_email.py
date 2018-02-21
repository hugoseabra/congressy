from behave import given, when, then
from selenium import webdriver
from nose.tools import *

@when('ele digitar o seu email no campo')
def step_impl (context):
    driver = context.browser
    form = driver.find_element_by_tag_name(tag='form-group')
    driver.find_element_by_name(form, name="email").send_keys('teste@me.com')
    form.submit()
@then ('A tela de login deve aparecer o campo email preenchido com o "{email}"')
def step_impl (context, email):
    driver = context.browser
    h = driver.find_element_by_id(id = 'email')
    eq_(h, email)
