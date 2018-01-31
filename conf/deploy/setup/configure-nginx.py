import sys
import os
from shutil import copyfile
from jinja2 import Template

domain = os.environ.get('DOMAIN')
force_https = os.environ.get('FORCE_HTTPS')

if not domain:
    msg = "DOMAIN not provided or misconfigured."
    print(msg)
    sys.exit(1)

# create dictionary of environment variables
env_dict = {
    'DOMAIN': domain,
    'FORCE_HTTPS': force_https is True,
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
    '/var/www/cgsy/conf/deploy/templates/nginx-cgsy.j2',
    '/etc/nginx/sites-available/default'
)
