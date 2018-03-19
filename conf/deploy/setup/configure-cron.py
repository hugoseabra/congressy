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
    sys.exit(1)

CRON_IN = os.getenv('CRON_SYNC_MINUTES_IN')
CRON_SYNC_MINUTES_IN = CRON_IN if len(CRON_IN) > 0 else 5

CRON_OUT = os.getenv('CRON_SYNC_MINUTES_OUT')
CRON_SYNC_MINUTES_OUT = CRON_OUT if len(CRON_OUT) > 0 else 8

# create dictionary of environment variables
env_dict = {
    'CRON_SYNC_MINUTES_IN': CRON_SYNC_MINUTES_IN,
    'CRON_SYNC_MINUTES_OUT': CRON_SYNC_MINUTES_OUT,
    'BUCKET_NAME': os.getenv('BUCKET_NAME', default_bucket_name),
}

# Crontab
setup(
    env_dict,
    '/var/www/cgsy/conf/deploy/templates/crontab.j2',
    '/crontab.txt'
)
