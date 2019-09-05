#!/bin/bash
set -e

source ../../common/common.sh

docker-compose up -d --build --force-recreate
