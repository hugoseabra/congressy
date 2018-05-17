from behave import when,then
import time
from nose.tools import eq_

@when('Clica em ja possui conta')
def step_impl(context):
    driver = context.browser
    reset_button = driver.find_element_by_css_selector('.help-block > a:nth-child(2)')
    reset_button.click()
    time.sleep(1)
@then('Usuario entra na pagina de login')
def step_impl(context):
    driver = context.browser
    assert driver.current_url.endswith('/login/')
    h1 = driver.find_element_by_css_selector('.panel-title').text
    eq_(h1, 'LOGIN')

