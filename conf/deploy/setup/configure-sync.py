import os
import sys
from shutil import copyfile

from jinja2 import Template

aws_key = os.environ.get('AWS_KEY')
aws_secret = os.environ.get('AWS_SECRET')
bucketname = os.environ.get('BUCKET_NAME')
default_bucket_name = 'cgsyplatform'

if not aws_key or not aws_secret:
    msg = "AWS credentials not provided or misconfigured:" \
          " -e AWS_KEY=key -e AWS_SECRET=secret"
    print(msg)
    sys.exit(1)

if not bucketname:
    msg = "Bucket name (BUCKET_NAME) not provided or misconfigured." \
          " Assuming default: {}".format(default_bucket_name)
    print(msg)
    sys.exit(1)


CRON_IN = os.getenv('CRON_SYNC_MINUTES_IN')
CRON_SYNC_MINUTES_IN = CRON_IN if len(CRON_IN) > 0 else 5

CRON_OUT = os.getenv('CRON_SYNC_MINUTES_OUT')
CRON_SYNC_MINUTES_OUT = CRON_OUT if len(CRON_OUT) > 0 else 8


# create dictionary of environment variables
env_dict = {
    'AWS_KEY': aws_key,
    'AWS_SECRET': aws_secret,
    'BUCKET_LOCATION': os.environ.get('BUCKET_LOCATION', 'us-east-1'),
    'CRON_SYNC_MINUTES_IN': CRON_SYNC_MINUTES_IN,
    'CRON_SYNC_MINUTES_OUT': CRON_SYNC_MINUTES_OUT,
    'BUCKET_NAME': os.environ.get('BUCKET_NAME', default_bucket_name),
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


# Crontab
setup(
    '/var/www/cgsy/conf/deploy/templates/crontab.j2',
    '/crontab.txt'
)

# Configures s3
setup(
    '/var/www/cgsy/conf/deploy/templates/s3bucket.j2',
    '/s3bucket.sh'
)

# in-sync configuration
setup(
    '/var/www/cgsy/conf/deploy/templates/in-sync.j2',
    '/in-sync.sh'
)

# setup s3cmd
setup(
    '/var/www/cgsy/conf/deploy/templates/s3cfg.j2',
    '/root/.s3cfg'
)
