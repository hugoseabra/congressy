import os
import django
from selenium import webdriver

language = 'pt-BR'
browser = 'chrome'

from selenium.webdriver.chrome.options import Options
# This is necessary for all installed apps to be recognized, for some reason.
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings.dev'


def before_all(context):
    # Even though DJANGO_SETTINGS_MODULE is set, this may still be
    # necessary. Or it may be simple CYA insurance.
    django.setup()

    ### Take a TestRunner hostage.
    from django.test.runner import DiscoverRunner
    # We'll use thise later to frog-march Django through the motions
    # of setting up and tearing down the test environment, including
    # test databases.
    context.runner = DiscoverRunner()

    ## If you use South for migrations, uncomment this to monkeypatch
    ## syncdb to get migrations to run.
    # from south.management.commands import patch_for_test_db_setup
    # patch_for_test_db_setup()

    ### Set up the WSGI intercept "port".
    # import wsgi_intercept
    # from django.core.handlers.wsgi import WSGIHandler
    # host = context.host = '0.0.0.0'
    # # port = context.port = getattr(settings, 'TESTING_MECHANIZE_INTERCEPT_PORT', 17681)
    # port = context.port = 8001
    # # NOTE: Nothing is actually listening on this port. wsgi_intercept
    # # monkeypatches the networking internals to use a fake socket when
    # # connecting to this port.
    # wsgi_intercept.add_wsgi_intercept(host, port, WSGIHandler)

    # def browser_url(url):
    #     """Create a URL for the virtual WSGI server.
    #
    #     e.g context.browser_url('/'), context.browser_url(reverse('my_view'))
    #     """
    #     return urljoin('http://%s:%d/' % (host, port), url)
    #
    # context.browser_url = browser_url

    ### BeautifulSoup is handy to have nearby. (Substitute lxml or html5lib as you see fit)
    from bs4 import BeautifulSoup

    def parse_soup():
        """Use BeautifulSoup to parse the current response and return the DOM tree.
        """
        r = context.browser.response()
        html = r.read()
        r.seek(0)
        return BeautifulSoup(html)

    # Set up the scenario test environment
    # context.runner.setup_test_environment()
    # We must set up and tear down the entire database between
    # scenarios. We can't just use db transactions, as Django's
    # TestClient does, if we're doing full-stack tests with Mechanize,
    # because Django closes the db connection after finishing the HTTP
    # response.
    # context.old_db_config = context.runner.setup_databases()


    context.parse_soup = parse_soup


def before_scenario(context, scenario):
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

    ### Set up the Mechanize browser.
    # MAGIC: All requests made by this monkeypatched browser to the magic
    # host and port will be intercepted by wsgi_intercept via a
    # fake socket and routed to Django's WSGI interface.
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


def after_all(context):
    context.browser.quit()

#def after_all(context):
    # Tear down the scenario test environment.
    #context.runner.teardown_databases(context.old_db_config)
    #context.runner.teardown_test_environment()
    # Bob's your uncle.