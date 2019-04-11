#!/usr/bin/env bash


# Tell uWSGI where to find your wsgi file (change this:
export UWSGI_CHDIR=/code/
export UWSGI_PYTHONPATH=/code/
export UWSGI_FILE=/code/project/wsgi.py
#export UWSGI_MODULE=project.wsgi:application

export UWSGI_SOCKET=127.0.0.1:49152
export UWSGI_HTTP=:8000
export UWSGI_MASTER=1
export UWSGI_HTTP_AUTO_CHUNKED=1
export UWSGI_HTTP_KEEPALIVE=1
export UWSGI_UID=1000
export UWSGI_GID=2000
export UWSGI_LAZY_APPS=1
export UWSGI_WSGI_ENV_BEHAVIO=holy
export UWSGI_HARAKIRI=20

# uWSGI static file serving configuration (customize or comment out if not needed_:
export UWSGI_STATIC_MAP="/static/=/code/static/"
export UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"

# Number of uWSGI workers and threads per worker (customize as needed:
export UWSGI_WORKERS=2
export UWSGI_THREADS=4
