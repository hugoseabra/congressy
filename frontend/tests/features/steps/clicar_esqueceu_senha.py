from behave import when, then
import time
from nose.tools import eq_

@when('Clica em esqueceu senha')
def step_impl (context):
    driver = context.browser
    reset_button = driver.find_element_by_css_selector('div.text-right:nth-child(1) > a:nth-child(1)')
    reset_button.click()
    time.sleep(4)

@then ('Ele entra na pagina de resetar senha')
def step_impl (context):
    driver = context.browser
    assert driver.current_url.endswith('/reset-password/')
    h1 = driver.find_element_by_css_selector('h3.panel-title').text
    eq_(h1, 'RECUPERAR CONTA')