#!/usr/bin/env bash
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

BASE=$(dirname "$0")
echo "${BASE}/tagged_version"
CHECKABLE_FILE=$(cat ${BASE}/tagged_version)


if [ "$CHECKABLE_FILE" == "1" ]; then
    VERSION=$(cat "$BASE/../../../version")
    docker exec -i awsecr cgsy:${VERSION}
fi
