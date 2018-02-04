#!/usr/bin/env bash
set -ex
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: publicar imagens de produção
#
# Busca a última com versão (padrão semver) mais alta e compara com a versão
# do build. Se diferente e maior, construir.
###############################################################################

function version {
    echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }';
}

LAST_IMAGE=$(docker exec awsecr last-image cgsy)
PATTERN="Repository: cgsy"
PATTERN2="871800672816.dkr.ecr.us-east-1.amazonaws.com/cgsy:"
LAST_VERSION=${LAST_IMAGE//"$PATTERN"/""}
LAST_VERSION=${LAST_IMAGE//"$PATTERN2"/""}

VERSION=$(cat ../../../version)

if [ $(version $LAST_VERSION) -gt $(version $VERSION) ]; then
    echo "Construindo imagem com versão '$LAST_VERSION' ..."
    docker exec awsecr push cgsy:${LAST_VERSION}
elif [ $(version $VERSION) -lt $(version $LAST_IMAGE) ]; then
    echo "A versão '$LAST_VERSION' é mais antiga do que '$VERSION' e não será publicada."
else
    echo "A versão '$LAST_VERSION' e '$VERSION' são idênticas e, portanto, não será publicada."
fi
