from behave import given

@given('Usuario entra na pagina de registro')
def step_impl(context):
    context.browser.get('http://0.0.0.0:8001/register/')