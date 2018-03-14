from behave import given, then, when
from nose.tools import eq_
import time
from selenium.common.exceptions import NoSuchElementException



@given('Usuario logado na pagina eventos')
def step_impl(context):
    driver = context.browser
    context.browser.get('http://0.0.0.0:8001/login/')
    email = driver.find_element_by_id('email')
    email.send_keys('ana.carolina@me.com')
    senha = driver.find_element_by_id('password')
    senha.send_keys('123')
    driver = context.browser
    login_button = driver.find_element_by_tag_name('button')
    login_button.click()
    djToolBar = driver.find_element_by_css_selector('#djHideToolBarButton')
    djToolBar.click()
    eventos = driver.find_element_by_css_selector('li.dropdown:nth-child(3)')
    eventos.click()
@when('Clica no evento \'{evento}\'')
def step_impl(context,evento):
    driver = context.browser
    link ='#event_table > tbody > tr:nth-child('+evento+') > td.sorting_1 > a'
    evento = driver.find_element_by_css_selector(link)
    evento.click()

@when('Usuario vai para pagina de editar o evento e clica para visualizar pagina')
def step_impl(context):
    driver = context.browser
    btn = driver.find_element_by_css_selector('a.btn')
    btn.click()
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])

@then('Aparece o titulo')
def step_impl(context):
    driver = context.browser
    titulo = driver.find_element_by_css_selector('.hero-title').is_displayed()
    eq_(titulo,True)

@then('Aparece a data do evento')
def step_impl(context):
    driver = context.browser
    campo_data = driver.find_element_by_css_selector('.col-md-offset-1 > div:nth-child(3)').is_displayed()
    eq_(campo_data,True)

@then('A descricao rapida \'{flag}\'')
def step_impl(context, flag):
    driver = context.browser
    try:
        campo_descricao = driver.find_element_by_css_selector('.lead').is_displayed()
    except NoSuchElementException:
        if(flag == 'não existe'):
            return True
        else:
            False


@then('A mensagem de Inscrições encerradas')
def step_impl(context):
    driver = context.browser
    campo_mensagem = driver.find_element_by_css_selector('.hero-features-left > p:nth-child(2)').is_displayed()
    eq_(campo_mensagem,True)

@then('Aparece descricao do evento')
def step_impl(context):
    driver = context.browser
    campo_mensagem = driver.find_element_by_css_selector('.about-text').is_displayed()
    eq_(campo_mensagem, True)

@then('Existe o campo de descricao do organizador')
def step_impl(context):
    driver = context.browser
    campo_mensagem = driver.find_element_by_css_selector('#owner > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').is_displayed()
    eq_(campo_mensagem, True)

@then('Existe o bloco de inscricao')
def step_impl(context):
    driver = context.browser
    campo_mensagem = driver.find_element_by_css_selector('.form').is_displayed()
    eq_(campo_mensagem, True)

@then('Existe o botao para fazer a inscricao')
def step_impl(context):
    driver = context.browser
    campo_mensagem = driver.find_element_by_css_selector('button.btn').is_displayed()
    eq_(campo_mensagem, True)

@then('Existe o bloco do banner')
def step_impl(context):
    driver = context.browser
    if(driver.find_element_by_css_selector('.img-responsive')):
        return True
    return False

@then('Existe o lote \'{lote}\'')
def step_impl(context,lote):
    driver = context.browser
    path = '.icon-list > li:nth-child('+lote+')'
    campo_mensagem = driver.find_element_by_css_selector(path).is_displayed()
    eq_(campo_mensagem, True)

@when('Rola a pagina ate o fim')
def step_impl(context):
    driver = context.browser
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
