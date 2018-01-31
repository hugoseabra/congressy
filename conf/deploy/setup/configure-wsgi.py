import os
from shutil import copyfile

from jinja2 import Template

# create dictionary of environment variables
env_dict = {
    'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'prod'),
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
    '/var/www/cgsy/conf/deploy/templates/wsgi.j2',
    '/var/www/cgsy/project/wsgi.py'
)
