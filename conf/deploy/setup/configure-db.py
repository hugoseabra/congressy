import os
from shutil import copyfile
from jinja2 import Template

dbname = os.environ.get('DBNAME')
dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbport = os.environ.get('DBPORT', 5432)

if not dbhost or not dbuser or not dbpass or not dbname:
    raise Exception(
        "DB credentials not provided or misconfigured:"
        " -e DBHOST=host -e DBUSER=user -e DBPASS=password -e DBNAME=dbname"
        " -e DBPORT=5432"
    )

# create dictionary of environment variables
env_dict = {
    'DBNAME': dbname,
    'DBUSER': dbuser,
    'DBPASS': dbpass,
    'DBHOST': dbhost,
    'DBPORT': dbport,
}


# function to add environment variables to file
def add_env_variables(content):
    content = Template(content)
    return content.render(env_dict)


def setup(origin_file_path, file_path):
    copyfile(origin_file_path, file_path)

    with open(file_path) as in_file:
        text = in_file.read()
        in_file.close()

    with open(file_path, 'w') as out_file:
        out_file.write(add_env_variables(text))
        out_file.close()


setup(
    '/var/www/cgsy/conf/deploy/templates/settings_prod.j2',
    '/var/www/cgsy/project/settings/prod.py'
)
