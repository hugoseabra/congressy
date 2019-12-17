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
echo "SAVING HOTSITE VERSION";
echo "###########################################################"
echo;

BASE=$(dirname $(dirname $(dirname "$0")))
VERSION_FILE="$BASE/hotsite-version"
PREVIOUS_VERSION_FILE="$BASE/previous_hotsite_version"
PREVIOUS_VERSION="latest"
VERSION="latest"

if [[ -f "$PREVIOUS_VERSION_FILE" ]]; then
    PREVIOUS_VERSION=$(cat ${PREVIOUS_VERSION_FILE})
fi

if [[ -f "$VERSION_FILE" ]]; then
    VERSION=$(cat ${VERSION_FILE})
fi

echo "Download versão '${VERSION}' sobre a versão '${PREVIOUS_VERSION}'..."

# A versão nunca será a anterior a atual devido ao CI controlar a continuidade
# dos releases. Sendo assim, basta comparar
if [[ "$PREVIOUS_VERSION" != "$VERSION" ]]; then

    echo "Baixando ${VERSION}' ..."
    docker exec -i awsecr pull hotsite-v2:${VERSION}

    echo "###########################################################"
    echo "DOWNLOAD FINISHED";
    echo "###########################################################"
    echo;

    # Sucesso
    exit 0

else
    echo "###########################################################"
    echo "DOWNLOAD FAILED";
    echo "###########################################################"
    echo;
    echo "Download não realizado '${VERSION}' ==  '${PREVIOUS_VERSION}'"
    echo;

    # Erro: versão já está publicada.
    exit 1
fi
