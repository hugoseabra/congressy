import os
import sys

sys.path.append("..")

from scripts import setup

bucketname = os.getenv('BUCKET_NAME')
default_bucket_name = 'cgsyplatform'

if not bucketname:
    msg = "Bucket name (BUCKET_NAME) not provided or misconfigured." \
          " Assuming default: {}".format(default_bucket_name)
    print(msg)

# create dictionary of environment variables
env_dict = {
    'BUCKET_NAME': os.getenv('BUCKET_NAME', default_bucket_name),
}

# Crontab
setup(
    env_dict,
    '/var/www/cgsy/conf/deploy/templates/crontab.j2',
    '/crontab.txt'
)
