#!/usr/bin/env bash
set -e

PGPASSWORD=4UnADjyMjeeB7GSc pg_dump \
  --format=c \
  --host congressy.cy6gssymlczu.us-east-1.rds.amazonaws.com \
  --port 5499 \
  --username congressy \
  --verbose \
  cgsyplatform > /tmp/backup/backup.sql