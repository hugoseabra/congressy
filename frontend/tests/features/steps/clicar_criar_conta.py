from behave import when, then
import time
from nose.tools import eq_

@when('Clica em criar conta')
def step_impl (context):
    driver = context.browser
    login_button = driver.find_element_by_css_selector('div.secondary-links:nth-child(1) > div:nth-child(1) > a:nth-child(1)')
    login_button.click()
    time.sleep(4)

@then ('Ele entra na pagina de registro')
def step_impl (context):
    driver = context.browser
    assert driver.current_url.endswith('/register/')
    h1 = driver.find_element_by_css_selector('h3.panel-title').text
    eq_(h1, 'NOVA CONTA')