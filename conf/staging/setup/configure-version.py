import os
from shutil import copyfile

from jinja2 import Template


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
    '/var/www/cgsy/conf/staging/templates/footer.j2',
    '/var/www/cgsy/frontend/templates/base/footer.html'
)

setup(
    '/var/www/cgsy/project/settings/common.py',
    '/var/www/cgsy/project/settings/common.py'
)
