#!/usr/bin/env sh

##############################################################################
# CUIDADO!
# Esta script será executado dentro do container do postgres.
##############################################################################

docker-compose -f /tmp/bkp/docker-compose.yml down
docker-compose -f ./bin/dev/docker-compose.yml up -d