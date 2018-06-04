#!/usr/bin/env sh
set -ex
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
    echo -e "${RED}$1${NC}"
    echo ;
    echo ;
}

function update_postgres_service() {
    docker-compose -f ./bin/env/docker-compose.yml up -d
    sleep 10

    local RUNNING=$(docker inspect -f {{.State.Running}} cgsy-postgres)
    if [ "$RUNNING" == "false" ]; then
        error_msg "Container não subiu."
        exit 1
    fi
}

BKP_DIR="/tmp/bkp"
BKP_DUMP_DIR="$BKP_DIR/backup"

CONTAINER_NAME="cgsy-postgres"

CONTAINER_ACTIVE=$(docker ps -qf name=${CONTAINER_NAME})
RECREATE=$(cat ${BKP_DUMP_DIR}/recreate.txt)

# Se container do Banco de dados não existe e está configurado para
# "não recriar", temos de vamos garantir que o serviço esteja ativo.

# Se não há container ativo, verificar se existe.
if [ -z "$CONTAINER_ACTIVE" ]; then

    # Verificar nos containers desativados.
    CONTAINER_EXISTS=$(docker ps -aqf name=${CONTAINER_NAME})

    if [ -z "$CONTAINER_EXISTS" ]; then
        if [ "$RECREATE" == "0" ]; then
            echo "Container '${CONTAINER_NAME}' não existe. Criando ..."
            update_postgres_service
        fi

    # Se existe, garantir que esteja ativo
    else
        echo "Container '${CONTAINER_NAME}' já existe. Ativando-o ..."
        docker-compose -f ./bin/env/docker-compose.yml start
    fi
else
    echo "Container '${CONTAINER_NAME}' está ativo."
fi

# Se será recriado, tudo certo.
if [ "$RECREATE" == "1" ]; then
    echo "Recriando banco de dados."

    # o docker-compose do staging pode depender de um env-file que pode não
    # existir
    touch ./bin/env/staging/env-manage-staging

    # manage-staging depende da rede criada pelo stack do banco. Devemos ter
    # certeza que o container não está rodando para destruir o banco, caso
    # contrário, o Docker não irá destruir informando que há um container
    # utilizando a rede.
    docker-compose -f ./bin/env/staging/docker-compose.yml down --remove-orphans

    # Mata image e destroi rede, volumes e container
    docker-compose -f ./bin/env/docker-compose.yml down --remove-orphans

    # Recria tudo novamente
    update_postgres_service
else
    echo "Os dados do banco de dados não foram resetados."
fi
