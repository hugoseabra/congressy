import os
from shutil import copyfile
from jinja2 import Template

aws_key = os.environ.get('AWS_KEY')
aws_secret = os.environ.get('AWS_SECRET')
bucketname = os.environ.get('BUCKET_NAME')
default_bucket_name = 'cgsyplatform'

if not aws_key or not aws_secret:
    raise Exception(
        "AWS credentials not provided or misconfigured:"
        " -e AWS_KEY=key -e AWS_SECRET=secret"
    )

if not bucketname:
    raise Exception(
        "Bucket name (BUCKET_NAME) not provided or misconfigured."
        " Assuming default: {}".format(default_bucket_name)
    )


# create dictionary of environment variables
env_dict = {
    'AWS_KEY': aws_key,
    'AWS_SECRET': aws_secret,
    'BUCKET_LOCATION': os.environ.get('BUCKET_LOCATION', 'us-east-1'),
    'CRON_SYNC_MINUTES_IN': os.environ.get('CRON_SYNC_MINUTES_IN', 5),
    'CRON_SYNC_MINUTES_OUT': os.environ.get('CRON_SYNC_MINUTES_OUT', 8),
    'BUCKET_NAME': os.environ.get('BUCKET_NAME', default_bucket_name),
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
