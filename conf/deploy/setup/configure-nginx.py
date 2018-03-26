import os
import sys

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

setup(
    env_dict,
    '/var/www/cgsy/conf/deploy/templates/nginx-cgsy.j2',
    '/etc/nginx/sites-available/default'
)
