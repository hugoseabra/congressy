#!/usr/bin/env sh
set -e
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Salvar versão de produção (branch master)
#
# Este script é para ser executado quando há commit no branch "master". Ele
# pega a última tag do projeto e persiste em um arquivo para ser usado em outro
# build para construir uma imagem com tag do docker.
#
# - Pega a úlima tag de referência: refs/tags/<tag: x.y.z>
# - Pega somente o número da tag (<tag: x.y.z>);
# - Persiste em um arquivo
#   (01_potsgres-db-restore.sh) para o local onde será construído o volume do
#   container.
###############################################################################

BASE=$(dirname "$0")

REF_TAG=$(git for-each-ref refs/tags --sort=-taggerdate --format='%(refname)' --count=1)
LAST_TAG=$(basename ${REF_TAG})

echo "$LAST_TAG" > ${BASE}/last_tag.txt

cat ${BASE}/last_tag.txt