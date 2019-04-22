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

# Configure traefik
docker-compose -f ./conf/staging/docker-compose.yml up -d --force --remove-orphans --scale manage=2

RUNNING=$(docker inspect -f {{.State.Running}} manage-staging)
if [[ "$RUNNING" != "true" ]]; then
    error_msg "Container do manage não subiu."
    exit 1
fi
