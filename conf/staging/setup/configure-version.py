import os
import sys

sys.path.append("..")

from scripts import setup


def read_file(file_path):
    if not os.path.exists(file_path):
        return ''

    with open(file_path) as f:
        content = f.read()
        f.close()

        return content.rstrip('\r\n')


env_dict = {
    'APP_VERSION': read_file('/var/www/cgsy/version'),
    'BUILD': read_file('/var/www/cgsy/build_number'),
    'BUILD_LINK': read_file('/var/www/cgsy/build_link'),
    'AUTHOR': read_file('/var/www/cgsy/build_author'),
}

setup(
    env_dict,
    '/var/www/cgsy/conf/staging/templates/footer.j2',
    '/var/www/cgsy/frontend/templates/base/footer.html'
)

setup(
    env_dict,
    '/var/www/cgsy/project/manage/settings/common.py',
    '/var/www/cgsy/project/manage/settings/common.py'
)
