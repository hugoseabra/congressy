#!/usr/bin/env sh
set -e

##############################################################################
# CUIDADO!
# Esta script será executado dentro do container do postgres.
##############################################################################

# Kill staging image because of dependency of network
docker-compose -f ./bin/env/staging/docker-compose.yml down

docker-compose -f ./bin/env/docker-compose.yml down
docker-compose -f ./bin/env/docker-compose.yml up -d