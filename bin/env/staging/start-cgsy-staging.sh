#!/usr/bin/env sh
set -e

##############################################################################
# CUIDADO!
# Esta script será executado dentro do container do postgres.
##############################################################################

docker-compose -f ./bin/env/staging/docker-compose.yml down
docker-compose -f ./bin/env/staging/docker-compose.yml up -d