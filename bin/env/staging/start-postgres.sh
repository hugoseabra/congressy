#!/usr/bin/env sh
set -e

##############################################################################
# CUIDADO!
# Esta script será executado dentro do container do postgres.
##############################################################################


BKP_PATH="/tmp/bkp/backup"
RECREATE=$(cat ${BKP_PATH}/recreate.txt)

if [ "$RECREATE" == "1" ]; then
    # o docker-compose do staging pode depender de um env-file que pode não
    # existir
    touch ./bin/env/staging/env-cgsy-staging

    # Kill staging image because of dependency of network
    docker-compose -f ./bin/env/staging/docker-compose.yml down

    docker-compose -f ./bin/env/docker-compose.yml down
    docker-compose -f ./bin/env/docker-compose.yml up -d
fi

