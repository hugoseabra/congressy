#!/usr/bin/env sh
set -e
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Criar/Ativar container do hugoseabra19/awsecr
#
# Este container facilita a publicação da imagem na AWSECR
#
# - Baixa imagem mais recente
# - Verifica se container existe
# - Se sim, Verifica se container está ativo
# - Se não existe, cria-o.
# - Se não ativo, ativa-o.
###############################################################################

BASE=$(dirname "$0")

IMAGE_NAME="hugoseabra19/awsecr"
CONTAINER_NAME="awsecr"

ENV_FILE_NAME="$BASE/env-awsecr"

CONTAINER_ACTIVE=$(docker ps -qf name=${CONTAINER_NAME})

if [ -z "$CONTAINER_ACTIVE" ]; then

    # Verificar nos containers desativados.
    CONTAINER_EXISTS=$(docker ps -aqf name=${CONTAINER_NAME})

    if [ -z "$CONTAINER_EXISTS" ]; then
        docker pull ${IMAGE_NAME}
        docker run --tid \
            --name ${CONTAINER_NAME} \
            --env-file ${ENV_FILE_NAME} \
            ${IMAGE_NAME}

    # Se existe, garantir que esteja ativo
    else
        echo "Container '${CONTAINER_NAME}' já existe. Ativando-o ..."
        docker start ${CONTAINER_NAME}
    fi
else
    echo "Container '${CONTAINER_NAME}' está ativo."
fi
