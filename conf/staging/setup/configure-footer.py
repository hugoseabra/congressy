import os
from shutil import copyfile
from jinja2 import Template

f = open('/var/www/cgsy/version')
app_version = f.read()
f.close()

f = open('/var/www/cgsy/build_number')
build_number = f.read()
f.close()

f = open('/var/www/cgsy/build_author')
build_author = f.read()
f.close()

env_dict = {
    'APP_VERSION': app_version.rstrip('\r\n'),
    'BUILD': build_number.rstrip('\r\n'),
    'AUTHOR': build_author.rstrip('\r\n'),
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
