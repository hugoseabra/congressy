from behave import given,then, when
from nose.tools import eq_

@given('Usuario entra na pagina de recuperar senha')
def step_impl(context):
    context.browser.get('http://0.0.0.0:8001/reset-password/')

@when('Ele entra na pagina de resetar senha')
def step_impl(context):
    driver = context.browser
    assert driver.current_url.endswith('/reset-password/')
    h1 = driver.find_element_by_css_selector('h3.panel-title').text
    eq_(h1, 'RECUPERAR CONTA')
