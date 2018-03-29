#!/usr/bin/env bash
set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pip install -r requirements_dev.pip

docker-compose -f $DIR/../docker-compose.yml down --remove-orphans
sleep 1

docker-compose -f $DIR/../docker-compose.yml up -d
sleep 8

# Removes previous media files
rm -rf $DIR/../../../media/*
