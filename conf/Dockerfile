# -----------------------------------------------------------------------------
# Docker IMAGE congressy/cgsy
# docker build --rm -t cgsy .
# docker tag catalog <repo_url>/catalog:<tag>
# -----------------------------------------------------------------------------
FROM python:3.6
MAINTAINER Hugo Seabra <hugoseabra19@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

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
ENV LANG pt_BR.UTF-

RUN localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8

RUN apt-get update -q && apt-get install -qy --no-install-recommends \
    build-essential \
    apt-transport-https \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    # Requerido pelo Postgresql Client
    libpq5 postgresql-client \
    # Nginx
    nginx \
    # Supervisor
    supervisor \
        && apt-get purge -y --auto-remove \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY ./conf/nginx.conf /etc/nginx/sites-available/default

# Supervisor
COPY ./conf/supervisor.conf /etc/supervisor/conf.d/

# install uwsgi now because it takes a little while
RUN pip install uwsgi celery[redis] lxml sparkpost

RUN mkdir -p /root/.pip
COPY ./conf/pip.conf /root/.pip/.

WORKDIR /var/www/cgsy

# Requirements
# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY ./requirements.pip ./.
RUN pip install -r requirements.pip

COPY ./ /var/www/cgsy/.
RUN python manage.py collectstatic --noinput

EXPOSE 80
CMD ["supervisord", "-n"]
