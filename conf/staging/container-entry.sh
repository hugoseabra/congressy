#!/usr/bin/env bash

# configures nginx
python /configure-nginx.py

# configures sync process workflow
python /configure-sync.py

chmod 777 /s3bucket.sh /in-sync.sh

# Verifies if bucket exists. If not, creates it.
/s3bucket.sh

# Runs in-sync: configuration state has priority of outsite if bucket exists
/in-sync.sh

# Configures database app credentials
python /configure-db.py

# Configures footer
python /configure-footer.py

python manage.py collectstatic --noinput

supervisord -n
