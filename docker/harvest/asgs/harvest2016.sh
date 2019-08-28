#!/bin/bash
set -e

source ../../../common/common.sh

docker-compose -f docker-compose.base.yml -f docker-compose.2016.yml up --build --force-recreate