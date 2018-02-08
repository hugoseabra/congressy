import os
import sys
from shutil import copyfile

from django.core.management.utils import get_random_secret_key
from jinja2 import Template

SENTRY_PUBLIC_DSN = os.environ.get('SENTRY_PUBLIC_DSN')
if not SENTRY_PUBLIC_DSN:
    print("SENTRY_PUBLIC_DSN not provided or misconfigured.")
    sys.exit(1)

# create dictionary of environment variables
env_dict = {
    'SENTRY_PUBLIC_DSN': SENTRY_PUBLIC_DSN,
}


# function to add environment variables to file
def add_env_variables(content):
    content = Template(content)
    return content.render(env_dict)


def setup(origin_file_path, file_path):
    if origin_file_path != file_path:
        copyfile(origin_file_path, file_path)

    with open(file_path) as in_file:
        text = in_file.read()
        in_file.close()

    with open(file_path, 'w') as out_file:
        out_file.write(add_env_variables(text))
        out_file.close()


setup(
    '/var/www/cgsy/frontend/templates/sentry_public_dsn.html',
    '/var/www/cgsy/frontend/templates/sentry_public_dsn.html'
)
