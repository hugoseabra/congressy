import os
import sys

sys.path.append(sys.path.append(os.path.dirname(os.path.dirname(__file__))))

from scripts import setup

aws_key = os.getenv('AWS_KEY')
aws_secret = os.getenv('AWS_SECRET')
bucketname = os.getenv('BUCKET_NAME')
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


# create dictionary of environment variables
env_dict = {
    'AWS_KEY': aws_key,
    'AWS_SECRET': aws_secret,
    'BUCKET_LOCATION': os.getenv('BUCKET_LOCATION', 'us-east-1'),
    'BUCKET_NAME': os.getenv('BUCKET_NAME', default_bucket_name),
}

# Configures s3
setup(
    env_dict,
    '/code/conf/deploy/templates/create-s3bucket.j2',
    '/create-s3bucket.sh'
)

# in-sync configuration
setup(
    env_dict,
    '/code/conf/deploy/templates/in-sync.j2',
    '/in-sync.sh'
)

# setup s3cmd
setup(
    env_dict,
    '/code/conf/deploy/templates/s3cfg.j2',
    '/root/.s3cfg'
)
