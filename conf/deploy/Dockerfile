# -----------------------------------------------------------------------------
# Docker IMAGE congressy/cgsy
# docker build --rm -t cgsy .
# docker tag catalog <repo_url>/cgsy:<tag>
# -----------------------------------------------------------------------------
FROM python:3.6
MAINTAINER Hugo Seabra <hugoseabra19@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

LABEL cgsy.image.name="cgsy-platform-production"

# -----------------------------------------------------------------------------
# Basics
RUN apt-get update -q && apt-get install -qy --no-install-recommends \
    apt-utils \
    nano \
    locales \
        && apt-get purge -y --auto-remove \
        && apt-get clean \
        && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/*

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
        && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/*

# -----------------------------------------------------------------------------
# Pypi packages

# install uwsgi now because it takes a little while
RUN pip install --no-cache-dir --upgrade \
        pip setuptools \
        # required by celery
        lxml \
        celery[redis] \
        # Celery UI
        flower \
        # send email
        sparkpost \
        uwsgi \
        # s3 synchronization
        s3cmd \
        # template engine
        jinja2 \
        # Sentry
        raven

RUN mkdir -p /root/.pip
COPY ./conf/deploy/pip.conf /root/.pip/.

# -----------------------------------------------------------------------------
# Nginx
COPY ./conf/deploy/nginx.conf /etc/nginx/nginx.conf

# -----------------------------------------------------------------------------
# Supervisor
COPY ./conf/deploy/supervisor.conf /etc/supervisor/conf.d/

# -----------------------------------------------------------------------------
WORKDIR /var/www/cgsy

# -----------------------------------------------------------------------------
# APP

# Requirements
# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY ./requirements.pip ./.
RUN pip install --no-cache-dir --upgrade -r requirements.pip

# -----------------------------------------------------------------------------
# Setup configuration files
COPY ./conf/deploy/scripts.sh /scripts.sh
COPY ./conf/deploy/scripts.py /scripts.py

COPY ./conf/deploy/setup/configure-settings.py /configure-settings.py
COPY ./conf/deploy/setup/configure-sync.py /configure-sync.py
COPY ./conf/deploy/setup/configure-cron.py /configure-cron.py
COPY ./conf/deploy/setup/configure-version.py /configure-version.py
COPY ./conf/deploy/setup/configure-wsgi.py /configure-wsgi.py
COPY ./conf/deploy/setup/configure-nginx.py /configure-nginx.py
COPY ./conf/deploy/services /services

# -----------------------------------------------------------------------------
COPY ./. ./.

RUN chmod 775 /services/volume/container-entry.sh \
              /services/migration/container-entry.sh \
              /services/cron/container-entry.sh \
              /services/web/manage/container-entry.sh \
              /services/web/partner/container-entry.sh \
              /services/web/admin/container-entry.sh

EXPOSE 80
