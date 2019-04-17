#!/usr/bin/env bash

# /bin/bash

STATUS_CODE=$(curl --write-out "%{http_code}\n" --silent --output /dev/null "http://localhost:8000/healthcheck/");

if [[ "$STATUS_CODE" -eq 200 ]] ; then
    echo "OK"
else
    echo "NOTOK"
    exit 1
fi
