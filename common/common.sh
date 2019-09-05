#!/bin/bash
set -e

SCRIPT_HOME=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

#import env vars to shell this is required in additon to env_file in some cases where variables need to be remapped
export $(grep -v '^#' ${SCRIPT_HOME}/common.env | sed '/^$/d' | xargs -0)