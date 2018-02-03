#!/usr/bin/env sh
set -e
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Gerenciar banco de dados de ambiente staging (RC)

# O backup será restaurado somente se houver um novo dump dia. Não há necessi-
# dade destruir o banco de dados do container se não há novo dump, mantendo os
# dados criados/modificados/deletados.
#
# - (Re)Cria banco de dados completo, caso o dump do dia seja novo.
# - Verifica se container realmente subiu.
#
# Importante: o CI constrói um volume compartilhado em /tmp/bkp que, por sua
# vez é utilizado no docker-compose. Isso fará o dump funcionar.
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

BKP_DIR="/tmp/bkp"
BKP_DUMP_DIR="$BKP_DIR/backup"

CONTAINER_EXISTS=$(docker ps -q -f name=cgsy-postgres)
RECREATE=$(cat ${BKP_DUMP_DIR}/recreate.txt)
RUNNING=$(docker inspect -f {{.State.Running}} cgsy-postgres)

# Caso container não exista OU não será recriado e não está rodando
if [ -z "$CONTAINER_EXISTS" ] || [ "$RECREATE" == "0" ] && [ "$RUNNING" != "true" ]; then
    docker-compose -f ./bin/env/docker-compose.yml up -d
    sleep 5

    if [ "$RUNNING" != "true" ]; then
        error_msg "Container não subiu."
        exit 1
    fi
fi

if [ "$RECREATE" == "1" ]; then
    echo "Recriando banco de dados."

    # o docker-compose do staging pode depender de um env-file que pode não
    # existir
    touch ./bin/env/staging/env-cgsy-staging

    # cgsy-staging depende da rede criada pelo stack do banco. Devemos ter
    # certeza que o container não está rodando para destruir o banco, caso
    # contrário, o Docker não irá destruir informando que há um container
    # utilizando a rede.
    docker-compose -f ./bin/env/staging/docker-compose.yml down

    # Mata image e destroi rede, volumes e container
    docker-compose -f ./bin/env/docker-compose.yml down

    # Recria tudo novamente
    docker-compose -f ./bin/env/docker-compose.yml up -d
    sleep 5

    RUNNING=$(docker inspect -f {{.State.Running}} cgsy-postgres)
    if [ "$RUNNING" != "true" ]; then
        error_msg "Container não subiu."
        exit 1
    fi
else
    echo "Banco de dados não será recriado."
fi