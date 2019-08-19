#!/bin/sh
set -e

source ../../common/common.sh

if [ -n "$1" ]
then
    if [ "$1" == "--rebuild" ]
    then
        export FORCE_REFRESH=1
    else
        echo "--rebuild is the only valid option to this script"
        exit 1
    fi
fi

docker-compose up -d --build --force-recreate

#Use this to see the logs if needed
#docker-compose logs -f