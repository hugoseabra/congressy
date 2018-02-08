import os
from shutil import copyfile
from jinja2 import Template


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
    '/var/www/cgsy/conf/deploy/templates/footer.j2',
    '/var/www/cgsy/frontend/templates/base/footer.html'
)
