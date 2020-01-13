#!/usr/bin/env sh
set -ex
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Destruir e (re)criar container de versão de staging.
###############################################################################
docker volume create staging_media
docker volume create staging_exporter
docker volume create staging_barcodes
docker volume create staging_qrcodes
docker volume create staging_vouchers
cat ./conf/deploy/traefik.toml
cp ./conf/deploy/traefik.toml /tmp/staging-files/.
cp ./conf/staging/docker-compose.yml /tmp/staging-files/.
docker-compose -f /tmp/staging-files/docker-compose.yml up -d --force --remove-orphans --scale manage=2
