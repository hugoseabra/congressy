import os
import django
from django.conf import settings
from selenium import webdriver

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings.dev'

BASE_DIR = settings.BASE_DIR
WEBDRIVERS_DIR = os.path.join(BASE_DIR, 'frontend', 'tests', 'web_drivers')
language = 'pt-BR'
browser = 'chrome'




def before_all(context):
    django.setup()


def before_scenario(context, scenario):
    if(browser=='opera'):
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=' + language)
        options.add_argument("--start-maximized")
        options.add_experimental_option('prefs', {'intl.accept_languages': language})
        options.binary_location = "/usr/bin/opera"
        opera_path = os.path.join(WEBDRIVERS_DIR, 'operadriver')
        context.browser = webdriver.Opera(executable_path= opera_path,options = options )
    elif(browser=='chrome'):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--lang='+language)
        chrome_options.add_argument('DJDT_DEBUG = True')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': language})
        chrome_path = os.path.join(WEBDRIVERS_DIR, 'chromedriver')
        context.browser =  webdriver.Chrome(executable_path= chrome_path, chrome_options=chrome_options)

    elif(browser == 'firefox'):
        firefox_path = os.path.join(WEBDRIVERS_DIR, 'geckodriver')
        firefox_bin_path = 'firefox'
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('intl.accept_languages', language)
        firefox_profile.update_preferences()
        context.browser = webdriver.Firefox(executable_path =firefox_path, firefox_binary=firefox_bin_path, firefox_profile=firefox_profile)

    context.browser.implicitly_wait(5)


def after_scenario(context,scenario):
    context.browser.quit()
