#!/usr/bin/env sh
set -e

###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: fazer deploy da última versão
#
# Este script será transferido e executado no(s) servidor(es) de produção.
# Ele irá verificar se a versão a ser publicada já está em produção e vai
# retornar um erro caso a versão já exista.
###############################################################################

echo "###########################################################"
echo "RUNNING MIGRATION";
echo "###########################################################"
echo;

BASE=$(dirname $(dirname $(dirname "$0")))
VERSION_FILE="$BASE/version"
PREVIOUS_VERSION_FILE="$BASE/previous_version"
PREVIOUS_VERSION="dev"
VERSION="dev"

if [[ -f "$PREVIOUS_VERSION_FILE" ]]; then
    PREVIOUS_VERSION=$(cat ${PREVIOUS_VERSION_FILE})
fi

if [[ -f "$VERSION_FILE" ]]; then
    VERSION=$(cat ${VERSION_FILE})
fi

# A versão nunca será a anterior a atual devido ao CI controlar a continuidade
# dos releases. Sendo assim, basta comparar
if [[ "$PREVIOUS_VERSION" != "$VERSION" ]]; then

    echo "Running migration for version ${VERSION}' ..."

    docker run --rm \
        --env-file=${BASE}/env-file \
        -v /etc/localtime:/etc/localtime \
        871800672816.dkr.ecr.us-east-1.amazonaws.com/cgsy:latest /deploy/services/migration/container-entry.sh

    echo ;

    echo "###########################################################"
    echo "MIGRATION FINISHED";
    echo "###########################################################"
    echo;

    # Sucesso
    exit 0

else
    echo "###########################################################"
    echo "ERROR ON MIGRATION";
    echo "###########################################################"
    echo;
    # Erro: versão já está publicada.
    exit 1
fi


