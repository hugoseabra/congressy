from behave import given, then, when
from nose.tools import eq_
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

path_inicial = 'http://0.0.0.0:8001/'
slugs = [
    'disponivel-disponivel/',
    'futuro-futuro/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-disponivel-e-1-nao-iniciado/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-disponivel-ilimitado/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-disponivel-limitado-5-vagas/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-disponivel-limitado-lotado/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-disponivel-limitado-lotado-e-1-disponivel-limitado-5-vagas/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-disponivel-limitado-lotado-e-1-nao-iniciado/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-expirado-e-1-disponivel-ilimitado/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-expirado-e-1-disponivel-limitado-5-vagas/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-expirado-e-1-disponivel-limitado-lotado/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-1-lote-nao-disponivel-data-futura/',
    'futuro-e-pago-c-lotes-com-transferencia-de-taxas-2-lotes-expirados/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-disponivel-e-1-nao-iniciado/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-disponivel-ilimitado/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-disponivel-limitado-5-vagas/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-disponivel-limitado-lotado/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-disponivel-limitado-lotado-e-1-disponivel-limitado-5-vagas/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-disponivel-limitado-lotado-e-1-nao-iniciado',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-expirado-e-1-disponivel-ilimitado/'
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-expirado-e-1-disponivel-limitado-5-vagas/'
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-expirado-e-1-disponivel-limitado-lotado/'
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-1-lote-nao-disponivel-data-futura/',
    'futuro-e-pago-c-lotes-sem-transferencia-de-taxas-2-lotes-expirados/',

]
@given ('Usuário entra no hotsite do evento \'{evento}\'')
def step_impl(context,evento):
    path = path_inicial+slugs[int(evento)-1]
    driver = context.browser
    driver.get(path)
    try:
        myElem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.hero-title')))

    except TimeoutException:
        print("Timed out waiting for page to load")

# @given('Usuario logado na pagina eventos')
# def step_impl(context):
#     driver = context.browser
#     context.browser.get('http://0.0.0.0:8001/login/')
#     email = driver.find_element_by_id('email')
#     email.send_keys('ana.carolina@me.com')
#     senha = driver.find_element_by_id('password')
#     senha.send_keys('123')
#     driver = context.browser
#     login_button = driver.find_element_by_tag_name('button')
#     login_button.click()
#     djToolBar = driver.find_element_by_css_selector('#djHideToolBarButton')
#     djToolBar.click()
#     eventos = driver.find_element_by_css_selector('li.dropdown:nth-child(3)')
#     eventos.click()
#
# @when('Clica no evento \'{evento}\'')
# def step_impl(context,evento):
#     driver = context.browser
#     evento = int(evento)
#     if(evento%10 !=0):
#         evento = evento % 10
#     else:
#         evento = str(10)
#     link ='#event_table > tbody > tr:nth-child({}) > td.sorting_1 > a'.format(evento)
#     evento = driver.find_element_by_css_selector(link)
#     evento.click()
#
# @when('Usuario vai para pagina de editar o evento e clica para visualizar pagina')
# def step_impl(context):
#     driver = context.browser
#     btn = driver.find_element_by_css_selector('a.btn')
#     btn.click()
#     time.sleep(5)
#     driver.switch_to.window(driver.window_handles[1])

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

@then('A descricao rapida')
def step_impl(context):
    driver = context.browser
    campo_descricao = driver.find_element_by_css_selector('.lead').is_displayed()
    eq_(campo_descricao, True)


# @then('A mensagem de Inscrições encerradas')
# def step_impl(context):
#     driver = context.browser
#     campo_mensagem = driver.find_element_by_css_selector('.hero-features-left > p:nth-child(2)').is_displayed()
#     eq_(campo_mensagem,True)

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

@then('\'{flag}\' o bloco de inscricao')
def step_impl(context, flag):
    driver = context.browser
    try:
        campo_mensagem = driver.find_element_by_css_selector('.form')
    except NoSuchElementException:
        assert(flag == 'Não possui')

    else:
        assert(flag == "Possui")


@then('\'{flag}\' o botao para fazer a inscricao')
def step_impl(context,flag):
    driver = context.browser
    try:
        campo_mensagem = driver.find_element_by_css_selector('button.btn')
    except NoSuchElementException:
        assert(flag == 'Não possui')
    else:
        assert(flag == "Possui")

@then('\'{flag}\' o campo nome')
def step_impl(context,flag):
    driver = context.browser
    try:
        campo_mensagem = driver.find_element_by_css_selector('#id_name')
    except NoSuchElementException:
        assert(flag == 'Não possui')
    else:
        assert(flag == "Possui")

@then('\'{flag}\' o campo email')
def step_impl(context,flag):
    driver = context.browser
    try:
        campo_mensagem = driver.find_element_by_css_selector('#id_email')
    except NoSuchElementException:
        assert(flag == 'Não possui')
    else:
        assert(flag == "Possui")
@then('O campo nome tem o tipo text')
def step_impl(context):
    driver = context.browser
    campo_input = driver.find_element_by_css_selector('#id_name').get_attribute('type')
    eq_(campo_input, 'text')

@then('O campo email tem o tipo email')
def step_impl(context):
    driver = context.browser
    campo_input = driver.find_element_by_css_selector('#id_email').get_attribute('type')
    eq_(campo_input, 'email')

@then('Existe o bloco do banner')
def step_impl(context):
    driver = context.browser
    if(driver.find_element_by_css_selector('.img-responsive')):
        return True
    return False

@then('\'{flag}\' o lote \'{lote}\'')
def step_impl(context,lote,flag):
    driver = context.browser
    path = '.icon-list > li:nth-child('+lote+')'
    try:
        campo_mensagem = driver.find_element_by_css_selector(path)
    except NoSuchElementException:
        assert (flag == 'Não possui')

    else:
        assert (flag == "Possui")


# @when('Rola a pagina ate o fim')
# def step_impl(context):
#     driver = context.browser
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# @then('Usuario ja esta logado aparece o botao de visualizar inscricao')
# def step_impl(context):
#     driver = context.browser
#     campo_mensagem = driver.find_element_by_css_selector('.btn-success').is_displayed()
#     eq_(campo_mensagem, True)

# @when('Clica para ir para a pagina \'{pagina}\'')
# def step_impl(context, pagina):
#     driver = context.browser
#     pagina = str(int(pagina) + 1)
#     path = 'li.paginate_button:nth-child('+pagina+') > a:nth-child(1)'
#     botao_pagina = driver.find_element_by_css_selector(path)
#     botao_pagina.click()

