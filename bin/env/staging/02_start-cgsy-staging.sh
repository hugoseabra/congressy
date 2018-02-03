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

docker-compose -f ./bin/env/staging/docker-compose.yml down
docker-compose -f ./bin/env/staging/docker-compose.yml up -d
sleep 5

echo ; echo ;
docker logs cgsy-staging
echo ; echo ;

RUNNING=$(docker inspect -f {{.State.Running}} cgsy-staging)
if [ "$RUNNING" != "true" ]; then
    echo "Container não subiu."
    exit 1
fi