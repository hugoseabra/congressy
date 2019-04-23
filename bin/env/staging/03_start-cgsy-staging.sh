#!/usr/bin/env sh
set -ex
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Destruir e (re)criar container de versão de staging.
#
# OBS: deve-se ter certeza que o container subiu.
###############################################################################
function error_msg() {
    local RED='\033[1;31m'
    local NC='\033[0m' # No Color
    echo ;
    echo ;
    echo -e "${RED}$1{NC}"
    echo ;
    echo ;
}

docker volume create staging_media
docker volume create staging_exporter
docker volume create staging_barcodes
docker volume create staging_qrcodes
docker volume create staging_vouchers
docker-compose -f ./conf/staging/docker-compose.yml up -d --force --remove-orphans --scale manage=2
