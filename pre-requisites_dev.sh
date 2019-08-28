#!/usr/bin/env bash

## RODE ESTE SCRIPT ANTES DE RODAR A INSTALAÇÃO DOS REQUIREMENTS EM AMBIENTE LOCAL

# On debian
sudo aptitude update
sudo aptitude install -y \
    build-essential \
    curl \
    libbz2-dev \
    libpcre3-dev \
    libpq-dev \
    libffi-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    liblcms2-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libtiff5-dev \
    libxml2-dev \
    libxslt-dev \
    libwebp-dev \
    llvm \
    make \
    postgresql-client \
    python-dev \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev

curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
