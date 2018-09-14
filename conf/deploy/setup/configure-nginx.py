import os
import sys
import tempfile

sys.path.append("..")

from scripts import setup

domain = os.environ.get('DOMAIN')
force_https = os.environ.get('FORCE_HTTPS')

force_https_values = ('true', '1',)
force_https = str(force_https).lower() in force_https_values

if not domain:
    msg = "DOMAIN not provided or misconfigured."
    print(msg)
    sys.exit(1)

# create dictionary of environment variables
env_dict = {
    'DOMAIN': domain,
    'FORCE_HTTPS': force_https is True,
}

# https://github.com/dockerfile/nginx/issues/4
# Create temp files for use of nginx
body_client = os.path.join(tempfile.gettempdir(), 'nginx', 'client_body')
proxy = os.path.join(tempfile.gettempdir(), 'nginx', 'proxy')
fastcgi = os.path.join(tempfile.gettempdir(), 'nginx', 'fastcgi')
uwsgi = os.path.join(tempfile.gettempdir(), 'nginx', 'uwsgi')

for path in [body_client, proxy, fastcgi, uwsgi]:
    if not os.path.exists(path):
        os.makedirs(path)

setup(
    env_dict,
    '/var/www/cgsy/conf/deploy/templates/nginx-cgsy.j2',
    '/etc/nginx/sites-available/default'
)
