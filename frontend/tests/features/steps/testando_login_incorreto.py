from behave import given, when, then
from nose.tools import eq_
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

@then('Ele nao ira conseguir logar e ira aparecer a mensagem \'{text}\'')
def step_impl (context, text):
    driver = context.browser
    alert_message = driver.find_element_by_css_selector('div.alert.alert-danger').text

    eq_(alert_message, text)

@then('Deve aparecer um captcha')
def step_impl(context):
    driver = context.browser
    driver.find_element_by_id('id_captcha_0')
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located(driver.find_element_by_id('id_captcha_0')))


