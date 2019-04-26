import os
import sys

sys.path.append(os.path.join('/', 'code', 'conf', 'deploy'))

from scripts import setup


def read_file(file_path):
    if not os.path.exists(file_path):
        return ''

    with open(file_path) as f:
        content = f.read()
        f.close()

        return content.rstrip('\r\n')


env_dict = {
    'APP_VERSION': read_file('/code/version'),
    'BUILD': read_file('/code/build_number'),
    'BUILD_LINK': read_file('/code/build_link'),
    'AUTHOR': read_file('/code/build_author'),
}

setup(
    env_dict,
    '/code/conf/staging/templates/footer.j2',
    '/code/frontend/templates/base/footer.html'
)

setup(
    env_dict,
    '/code/project/manage/settings/common.py',
    '/code/project/manage/settings/common.py'
)
