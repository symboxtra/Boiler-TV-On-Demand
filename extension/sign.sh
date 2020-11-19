#!/bin/bash

set -e

AMO_JWT_ISSUER="${1:-${AMO_JWT_ISSUER}}"
AMO_JWT_SECRET="${2:-${AMO_JWT_SECRET}}"

if [ -z "${AMO_JWT_ISSUER}" ]; then
    echo "Missing JWT issuer as argument 1 or env variable AMO_JWT_ISSUER."
    echo
    exit 1
elif [ -z "${AMO_JWT_SECRET}" ]; then
    echo "Missing JWT secret as argument 2 or env variable AMO_JWT_SECRET."
    echo
    exit 1
fi

web-ext sign --api-key="${AMO_JWT_ISSUER}" --api-secret="${AMO_JWT_SECRET}"
