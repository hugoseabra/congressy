from behave import when,then
from frontend.tests.features.steps.helpers import login
from nose.tools import eq_

@when('Usuario loga com  email \'{email}\' e senha \'{senha}\' e entra na pagina manage')
def step_impl(context, email, senha):
    driver = context.browser
    login.logar(context, email,senha)
    assert driver.current_url.endswith('/manage/')

@then('A pagina deve ter o logo')
def step_impl(context):
    driver = context.browser
    logo = driver.find_element_by_css_selector('.base_logo').is_displayed()
    eq_(logo, True)

@then('A pagina deve conter o campo do usuario no topo')
def step_impl(context):
    driver = context.browser
    logo = driver.find_element_by_css_selector('li.dropdown:nth-child(4) > a:nth-child(1) > span:nth-child(1)').is_displayed()
    eq_(logo, True)

@then('A pagina deve conter o titulo Minhas Inscricoes')
def step_impl(context):
    driver = context.browser
    h1 = driver.find_element_by_tag_name('h1').text
    eq_(h1, 'Minhas inscrições')

@when('Clica no seu perfil')
def step_impl(context):
    driver = context.browser
    perfil = driver.find_element_by_css_selector('li.dropdown:nth-child(1)')
    perfil.click()

@then('Deve descer um menu')
def step_impl(context):
    driver = context.browser
    menu = driver.find_elemes   nt_by_css_selector('li.dropdown:nth-child(4) > ul:nth-child(2)').is_displayed()
    eq_(menu,True)
