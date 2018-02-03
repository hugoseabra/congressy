#!/usr/bin/env sh
set -e
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
    echo -e "${RED}$RESULT${NC}"
    echo ;
    echo ;
}

docker-compose -f ./bin/env/staging/docker-compose.yml down
docker-compose -f ./bin/env/staging/docker-compose.yml up -d
sleep 10

echo ;
docker logs cgsy-staging
echo ;

RUNNING=$(docker inspect -f {{.State.Running}} cgsy-staging)
if [ "$RUNNING" != "true" ]; then
    error_msg "Container não subiu."
    exit 1
fi