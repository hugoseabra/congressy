#!/usr/bin/env bash

set -ex

REPO="congressy/cgsy"

drone secret add -repository ${REPO} -name AWS_KEY -value AKIAJHS7RBNESVTWWI6Q
drone secret add -repository ${REPO} -name AWS_SECRET -value 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
drone secret add -repository ${REPO} -name AWS_REGISTRY -value 871800672816.dkr.ecr.us-east-1.amazonaws.com
drone secret add -repository ${REPO} -name AWS_ACCOUNT_ID -value 871800672816
drone secret add -repository ${REPO} -name BUCKET_LOCATION -value us-east-1
drone secret add -repository ${REPO} -name BUCKET_NAME -value cgsyplatform

# Staging
drone secret add -repository ${REPO} -name DOMAIN_STAGING -value test.congressy.com
drone secret add -repository ${REPO} -name FORCE_HTTPS_STAGING -value True
drone secret add -repository ${REPO} -name DBHOST_STAGING -value cgsy-postgres
drone secret add -repository ${REPO} -name DBUSER_STAGING -value congressy
drone secret add -repository ${REPO} -name DBPASS_STAGING -value congressy
drone secret add -repository ${REPO} -name DBPORT_STAGING -value 5432

# Production
drone secret add -repository ${REPO} -name DOMAIN -value ev.congressy.com
drone secret add -repository ${REPO} -name FORCE_HTTPS -value True
drone secret add -repository ${REPO} -name DBHOST -value congressy.cy6gssymlczu.us-east-1.rds.amazonaws.com
drone secret add -repository ${REPO} -name DBUSER -value congressy
drone secret add -repository ${REPO} -name DBPASS -value 4UnADjyMjeeB7GSc
drone secret add -repository ${REPO} -name DBPORT -value 5499

drone secret add -repository ${REPO} -name CONGRESSY_DEPLOY -value @~/.ssh/congressy-deploy.pem
