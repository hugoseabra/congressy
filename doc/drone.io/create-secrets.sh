#!/usr/bin/env bash

set -ex

REPO="congressy/cgsy"

drone secret add ${REPO} AWS_KEY <key>
drone secret add ${REPO} AWS_SECRET <secret>
drone secret add ${REPO} AWS_REGISTRY 871800672816.dkr.ecr.us-east-1.amazonaws.com
drone secret add ${REPO} AWS_ACCOUNT_ID 871800672816
drone secret add ${REPO} BUCKET_LOCATION us-east-1
drone secret add ${REPO} BUCKET_NAME cgsyplatform

# Staging
drone secret add ${REPO} DOMAIN_STAGING test.congressy.com
drone secret add ${REPO} FORCE_HTTPS_STAGING True
drone secret add ${REPO} DBHOST_STAGING cgsy-postgres
drone secret add ${REPO} DBUSER_STAGING congressy
drone secret add ${REPO} DBPASS_STAGING congressy
drone secret add ${REPO} DBPORT_STAGING 5432

# Production
drone secret add ${REPO} DOMAIN ev.congressy.com
drone secret add ${REPO} FORCE_HTTPS True
drone secret add ${REPO} DBHOST congressy.cy6gssymlczu.us-east-1.rds.amazonaws.com
drone secret add ${REPO} DBUSER congressy
drone secret add ${REPO} DBPASS <pass>
drone secret add ${REPO} DBPORT 5499

drone secret add ${REPO} CONGRESSY_DEPLOY @ ~/.ssh/congressy-deploy.pem
