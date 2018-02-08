# -----------------------------------------------------------------------------
# Docker IMAGE congressy/cgsy
# docker build --rm -t cgsy .
# docker tag catalog <repo_url>/catalog:<tag>
# -----------------------------------------------------------------------------
FROM python:3.6
MAINTAINER Hugo Seabra <hugoseabra19@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

# Helps on collecting static and runserver
ENV DJANGO_SETTINGS_MODULE project.settings.staging

LABEL cgsy.image.name="cgsy-platform-staging"

# -----------------------------------------------------------------------------
# Basics
RUN apt-get update -q && apt-get install -qy --no-install-recommends \
    apt-utils \
    nano \
    locales \
        && apt-get purge -y --auto-remove \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Locales
ENV LC_ALL pt_BR.UTF-8
ENV LANG pt_BR.UTF-8

RUN localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8

# -----------------------------------------------------------------------------
RUN apt-get update -q && apt-get install -qy --no-install-recommends \
    build-essential \
    apt-transport-https \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    # Sincronização com S3
    cron \
    # Requerido pelo Postgresql Client
    libpq5 postgresql-client \
    # Nginx
    nginx \
    # Supervisor
    supervisor \
        && apt-get purge -y --auto-remove \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# -----------------------------------------------------------------------------
# Pypi packages

# STAGING
RUN pip install --no-cache-dir uwsgi lxml sparkpost s3cmd jinja2

# install uwsgi now because it takes a little while
RUN pip install --no-cache-dir \
        # required by celery
        lxml \
        # send email
        sparkpost \
        uwsgi \
        # s3 synchronization
        s3cmd \
        # template engine
        jinja2


RUN mkdir -p /root/.pip
COPY ./conf/deploy/pip.conf /root/.pip/.

# -----------------------------------------------------------------------------
# Nginx
COPY ./conf/deploy/nginx.conf /etc/nginx/nginx.conf

# -----------------------------------------------------------------------------
# Supervisor - STAGING
COPY ./conf/staging/supervisor.conf /etc/supervisor/conf.d/

# -----------------------------------------------------------------------------
WORKDIR /var/www/cgsy

# -----------------------------------------------------------------------------
# APP

# Requirements
# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY ./requirements.pip ./.
COPY ./requirements_dev.pip ./.
RUN pip install --no-cache-dir -r requirements_dev.pip

# -----------------------------------------------------------------------------
# Setup
COPY ./conf/deploy/setup/configure-nginx.py /configure-nginx.py

# Setup STAGING
COPY ./conf/staging/setup/configure-wsgi.py /configure-wsgi.py
COPY ./conf/staging/setup/configure-settings.py /configure-settings.py
COPY ./conf/staging/setup/configure-version.py /configure-version.py
COPY ./conf/staging/setup/configure-sync.py /configure-sync.py
COPY ./conf/staging/container-entry.sh /entry.sh

# -----------------------------------------------------------------------------
COPY ./. ./.

RUN chmod 775 /entry.sh

EXPOSE 80
CMD ["/entry.sh"]
