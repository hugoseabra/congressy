#!/usr/bin/env bash


set -ex

docker-compose -f $BASE_DIR/bin/dev/docker-compose.yml down
docker volume prune -f