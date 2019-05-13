import os
import sys

sys.path.append(sys.path.append(os.path.dirname(os.path.dirname(__file__))))

from scripts import setup


def read_file(file_path):
    if not os.path.exists(file_path):
        return ''

    with open('/code/version') as f:
        content = f.read()
        f.close()

        return content.rstrip('\r\n')


env_dict = {
    'APP_VERSION': read_file('/code/version'),
    'COPYRIGHT_YEAR': datetime.now().strftime('%Y'),
}

setup(
    env_dict,
    '/code/conf/deploy/templates/footer.j2',
    '/code/frontend/templates/base/footer.html'
)
