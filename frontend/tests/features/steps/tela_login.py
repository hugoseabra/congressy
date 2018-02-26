from behave import given, then, when
from nose.tools import eq_


@given('Usuario entra na pagina de login')
def step_impl(context):
    context.browser.get('http://0.0.0.0:8001/login/')


@when('Usuario vizualiza a tela')
def step_impl(context):
    pass


@then('O campo \'{campo}\' deve ter o tipo \'{tipo}\'')
def step_impl(context, campo, tipo):
    driver = context.browser
    campo_input = driver.find_element_by_css_selector(campo).get_attribute('type')
    eq_(campo_input, tipo)
