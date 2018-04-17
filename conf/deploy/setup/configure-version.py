import os
import sys

sys.path.append("..")

from scripts import setup


def read_file(file_path):
    if not os.path.exists(file_path):
        return ''

    with open('/var/www/cgsy/version') as f:
        content = f.read()
        f.close()

        return content.rstrip('\r\n')


env_dict = {
    'APP_VERSION': read_file('/var/www/cgsy/version'),
}

setup(
    env_dict,
    '/var/www/cgsy/conf/deploy/templates/footer.j2',
    '/var/www/cgsy/frontend/templates/base/footer.html'
)
