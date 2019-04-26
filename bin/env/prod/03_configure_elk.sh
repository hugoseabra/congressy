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
echo "CONFIGURING ELK DOCKER COMPOSE FILES";
echo "###########################################################"
echo;

BASE=$(dirname $(dirname $(dirname "$0")))

FILE_BEAT_FILE_PATH="$BASE/conf/deploy/ELK/filebeat/filebeat.docker.yml"
METRIC_BEAT_FILE_PATH="$BASE/conf/deploy/ELK/metricbeat/metricbeat.docker.yml"
