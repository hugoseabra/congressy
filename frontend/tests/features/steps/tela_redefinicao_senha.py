from behave import given,then, when
from nose.tools import assert_not_equal, eq_

@given('Usuario entra na pagina de redefinicao de senha pelo link \'{link}\' \'{state}\'')
def step_impl(context, link,state):
    context.browser.get(link)
    teste_expirar = 'Mg' in link
    if(state == 'expirado'):
        eq_(teste_expirar, False)
    elif (state == 'não expirado'):
        eq_(teste_expirar, True)


@then('A pagina deve ter o titulo de painel \'{titulo}\'')
def step_impl(context,titulo):
    driver = context.browser
    h3 = driver.find_element_by_css_selector('.panel-title').text
    eq_(h3, titulo)

@then('O texto \'{texto}\' em \'{label}\'')
def step_impl(context, texto,label):
    driver = context.browser
    p = driver.find_element_by_css_selector(label).text
    eq_(p, texto)

@then('Um botao com texto \'{texto}\'')
def step_impl(context, texto):
    driver = context.browser
    button = driver.find_element_by_css_selector('.btn')
    is_button = 'btn' in button.get_attribute('class')
    eq_(is_button, True)
    eq_(button.text, texto)


@then('Um campo do tipo \'{tipo}\' em \'{label}\'')
def step_impl(context, tipo, label):
    driver = context.browser
    campo_input = driver.find_element_by_css_selector(label).get_attribute('type')
    eq_(campo_input, 'password')

