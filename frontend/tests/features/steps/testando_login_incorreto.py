from behave import given, when, then
from nose.tools import eq_


@then('Ele nao ira conseguir logar e ira aparecer a mensagem erro')
def step_impl (context):
    driver = context.browser
    alert_message = driver.find_element_by_css_selector('div.alert.alert-danger').is_displayed()

    eq_(alert_message, True)

@then('Deve aparecer um captcha')
def step_impl(context):
    driver = context.browser
    teste = driver.find_element_by_id('id_captcha_1').is_displayed()
    eq_(teste, True)
    if driver.find_element_by_id('id_captcha_0'):
        return True
    return False

