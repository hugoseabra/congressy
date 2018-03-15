import os
import django
from selenium import webdriver

language = 'pt-BR'
browser = 'chrome'

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings.dev'


def before_all(context):
    django.setup()


def before_scenario(context, scenario):
    if(browser=='opera'):
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=' + language)
        options.add_argument("--start-maximized")
        options.add_experimental_option('prefs', {'intl.accept_languages': language})
        options.binary_location = "/usr/bin/opera"
        opera_path = '/home/gabriel/congressy/cgsy/frontend/tests/web_drivers/operadriver'
        context.browser = webdriver.Opera(executable_path= opera_path,options = options )
    elif(browser=='chrome'):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--lang='+language)
        chrome_options.add_argument('DJDT_DEBUG = True')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': language})
        chrome_path = '/home/gabriel/congressy/cgsy/frontend/tests/web_drivers/chromedriver'
        context.browser =  webdriver.Chrome(executable_path= chrome_path, chrome_options=chrome_options)

    elif(browser == 'firefox'):
        firefox_path = '/home/gabriel/congressy/cgsy/frontend/tests/web_drivers/geckodriver'
        firefox_bin_path = '/home/gabriel/Documentos/firefox/firefox'
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('intl.accept_languages', language)
        firefox_profile.update_preferences()
        context.browser = webdriver.Firefox(executable_path =firefox_path, firefox_binary=firefox_bin_path, firefox_profile=firefox_profile)

    context.browser.implicitly_wait(5)


def after_scenario(context,scenario):
    context.browser.quit()