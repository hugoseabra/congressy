#!/usr/bin/env bash

# https://uwsgi-docs.readthedocs.io/en/latest/UpgradingTo2.0.html?highlight=strict#strict-mode
export UWSGI_STRICT=1

# Tell uWSGI where to find your wsgi file (change this:
export UWSGI_CHDIR=/code/
export UWSGI_PYTHONPATH=/code/
export UWSGI_FILE=/code/project/wsgi.py

export UWSGI_SOCKET=127.0.0.1:49152

export UWSGI_HTTP=:8000
export UWSGI_HTTP_AUTO_CHUNKED=1
export UWSGI_HTTP_KEEPALIVE=1

export UWSGI_MASTER=1
#export UWSGI_UID=www-data
#export UWSGI_GID=root
export UWSGI_LAZY_APPS=1
export UWSGI_WSGI_ENV_BEHAVIOR=holy

export UWSGI_HARAKIRI=600
export UWSGI_POST_BUFFERING=8192

# By default uWSGI allocates a very small buffer (4096 bytes) for the headers
# of each request. If you start receiving “invalid request block size” in your
# logs, it could mean you need a bigger buffer. Increase it (up to 65535) with
# the buffer-size option.
export UWSGI_BUFFER_SIZE=65535

# By default, stdin is remapped to /dev/null on uWSGI startup. If you need a
# valid stdin (for debugging, piping and so on) add --honour-stdin.
export UWSGI_HONOUR_STDIN=1

# uWSGI static file serving configuration (customize or comment out if not needed_:
export UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"

# Number of uWSGI workers and threads per worker (customize as needed:
export UWSGI_WORKERS=2
export UWSGI_THREADS=4

# Socket to receive commands
export UWSGI_MASTER_FIFO=/tmp/fifo0