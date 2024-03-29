# -----------------------------------------------------------------------------
# Docker IMAGE congressy/cgsy
# docker build --rm -t cgsy .
# docker tag catalog <repo_url>/cgsy:<tag>
# -----------------------------------------------------------------------------
FROM python:3.6-slim

# Celery does not work with root unless you force it
ENV C_FORCE_ROOT true

LABEL cgsy.image.name="cgsy-platform-production"

# Install packages needed to run your application (not build deps):
#   mime-support -- for mime types when serving static files
#   postgresql-client -- for running database commands
# We need to recreate the /usr/share/man/man{1..8} directories first because
# they were clobbered by a parent image.
RUN set -ex \
    && RUN_DEPS=" \
        nano \
        mime-support \
        vim \
        locales \
        libpcre3 \
        postgresql-client \
        build-essential \
        libxml2 \
        curl \
        cron \
        tzdata \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Locales
ENV LC_ALL=pt_BR.UTF-8 LANG=pt_BR.UTF-8

RUN localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8

# -----------------------------------------------------------------------------
# Requirements - includes dev packages
COPY ./requirements.pip /requirements.pip
COPY ./requirements_staging.pip /requirements_staging.pip

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
# Correct the path to your production requirements file, if needed.
RUN set -ex \
    && BUILD_DEPS=" \
        build-essential \
        libpcre3-dev \
        libpq-dev \
        libtiff5-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libxml2-dev \
        libxslt-dev \
        python-dev \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip3 install -U pip \
    # Exclusive packages for production environment.
    && pip3 install --no-cache-dir -r /requirements_staging.pip \
    # Django packs, after pip to avoid unnecessary download
    && pip3 install --no-cache-dir -U \
        uwsgi==2.0.18 \
        raven==6.10 \
        sparkpost==1.3.6 \
        s3cmd==2.0.2 \
        jinja2==2.10.1 \
        django-uwsgi==0.2.2 \
        # documentação do admin
        docutils \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# -----------------------------------------------------------------------------
# Date time and timezone
#ENV TZ=America/Sao_Paulo
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# -----------------------------------------------------------------------------
# Setup configuration files
COPY ./conf/deploy /deploy

# Setup STAGING
COPY ./conf/staging /staging

# -----------------------------------------------------------------------------
WORKDIR /code/

# -----------------------------------------------------------------------------
COPY ./. ./.

RUN chmod +x /code/bin/env/healthcheck.sh \
            /staging/services/volume/container-entry.sh \
            /staging/services/migration/container-entry.sh \
            /staging/services/celery/container-entry.sh \
            /staging/services/cron/container-entry.sh \
            /staging/services/web/manage/container-entry.sh

RUN mkdir -p /code/media/; mkdir -p /tmp/exporter; mkdir -p /tmp/barcodes; mkdir -p /tmp/qrcodes;

# server will listen on this port
EXPOSE 8000
