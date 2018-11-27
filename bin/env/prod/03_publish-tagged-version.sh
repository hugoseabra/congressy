#!/usr/bin/env sh
set -ex

###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: publicar imagem com versão (tag) no AWS ECR
#
# Busca a última com versão (padrão semver) mais alta e compara com a versão
# do build. Se diferente e maior, construir.
###############################################################################
echo "###########################################################"
echo "PUBLISHING NEW VERSION TO REPOSITORY"
echo "###########################################################"
echo;

BASE=$(dirname "$0")
echo "${BASE}/tagged_version"
CHECKABLE_FILE=$(cat ${BASE}/tagged_version)

if [[ "$CHECKABLE_FILE" == "1" ]]; then
    VERSION=$(cat "$BASE/../../../version")

    echo "Pushing version '${VERSION}' to repository ..."

    docker exec -i awsecr push cgsy:latest
    docker exec -i awsecr push cgsy:${VERSION}
    docker system prune -f --filter 'label=cgsy.image.name=cgsy-platform-production'

    echo "###########################################################"
    echo "PUBLISHED NEW VERSION TO REPOSITORY"
    echo "###########################################################"
    echo;

else
    echo "###########################################################"
    echo "VERSION NOT PUBLISHED"
    echo "###########################################################"
    echo;

fi

