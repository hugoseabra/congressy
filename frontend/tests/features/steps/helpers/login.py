import time

def logar (context, email, senha):
    driver = context.browser
    campo_email = driver.find_element_by_id('email')
    campo_email.send_keys(email)

    campo_senha = driver.find_element_by_id('password')
    campo_senha.send_keys(senha)

    login_button = driver.find_element_by_tag_name('button')
    login_button.click()
    time.sleep(4)