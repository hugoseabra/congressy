import os
import sys
from datetime import datetime

sys.path.append('/deploy')
sys.path.append('/code')

from project import system
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
    'system_name': system.get_system_name(),
    'system_owner_link': system.get_system_owner_link(),
}

setup(
    env_dict,
    '/code/conf/deploy/templates/footer.j2',
    '/code/frontend/templates/base/footer.html'
)
