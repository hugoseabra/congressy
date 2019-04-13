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
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \

    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Locales
ENV LC_ALL=pt_BR.UTF-8 LANG=pt_BR.UTF-8

RUN localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8

# -----------------------------------------------------------------------------
RUN mkdir -p /root/.pip
COPY ./conf/deploy/pip.conf /root/.pip/.

COPY ./requirements.pip /requirements.pip

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
    && pip3 install --no-cache-dir -r /requirements.pip \
    # Django packs, after pip to avoid unnecessary download
    && pip3 install --no-cache-dir -U \
        uwsgi==2.0.18 \
        raven==6.10 \
        sparkpost==1.3.6 \
        s3cmd==2.0.2 \
        jinja2==2.10.1 \
        django-uwsgi==0.2.2 \
        django-uwsgi-cache==1.0.1 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# -----------------------------------------------------------------------------
# Setup configuration files
COPY ./conf/deploy /deploy

# -----------------------------------------------------------------------------
WORKDIR /code/

# -----------------------------------------------------------------------------
COPY ./. ./.

RUN chmod +x /deploy/services/volume/container-entry.sh \
              /deploy/services/migration/container-entry.sh \
              /deploy/services/celery/container-entry.sh \
              /deploy/services/cron/container-entry.sh \
              /deploy/services/web/manage/container-entry.sh \
              /deploy/services/web/partner/container-entry.sh \
              /deploy/services/web/admin_intranet/container-entry.sh

# server will listen on this port
EXPOSE 8000
