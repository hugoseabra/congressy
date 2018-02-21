from behave import given

@given('pagina de login')
def step_impl(context):
    context.browser.get('http://0.0.0.0:8001/login/')
