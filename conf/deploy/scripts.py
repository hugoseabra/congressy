from shutil import copyfile

from jinja2 import Template


# function to add environment variables to file
def add_env_variables(env_dict, content):
    content = Template(content)
    return content.render(env_dict)


def setup(env_dict, origin_file_path, file_path):
    if origin_file_path != file_path:
        copyfile(origin_file_path, file_path)

    with open(file_path) as in_file:
        text = in_file.read()
        in_file.close()

    with open(file_path, 'w') as out_file:
        out_file.write(add_env_variables(env_dict, text))
        out_file.close()
