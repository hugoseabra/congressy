#!/usr/bin/env sh
set -ex

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

BASE=$(dirname "$0")
VERSION_FILE="$BASE/version"
PREVIOUS_VERSION_FILE="$BASE/previous_version"
PREVIOUS_VERSION="dev"
VERSION="dev"

if [ -f "$PREVIOUS_VERSION_FILE" ]; then
    PREVIOUS_VERSION=$(cat ${PREVIOUS_VERSION_FILE})
fi

if [ -f "$VERSION_FILE" ]; then
    VERSION=$(cat ${VERSION_FILE})
fi

# A versão nunca será a anterior a atual devido ao CI controlar a continuidade
# dos releases. Sendo assim, basta comparar
if [ "$PREVIOUS_VERSION" != "$VERSION" ]; then
    docker exec -i awsecr pull cgsy:latest
    docker exec -i awsecr pull cgsy:${VERSION}
    docker-compose -f ~/cgsy/docker-compose.yml up -d --remove-orphans --force
    sleep 30

    echo ;
    docker system prune -f --filter 'label=cgsy.image.name=cgsy-platform-production'
    echo ;
    docker-compose -f ~/cgsy/docker-compose.yml logs redis
    docker-compose -f ~/cgsy/docker-compose.yml logs wkhtmltopdf
    docker-compose -f ~/cgsy/docker-compose.yml logs migration
    docker-compose -f ~/cgsy/docker-compose.yml logs volume
    docker-compose -f ~/cgsy/docker-compose.yml logs cron
    docker-compose -f ~/cgsy/docker-compose.yml logs manage
    docker-compose -f ~/cgsy/docker-compose.yml logs partner
    echo ;

    # Sucesso
    exit 0

else
    # Erro: versão já está publicada.
    exit 1
fi
