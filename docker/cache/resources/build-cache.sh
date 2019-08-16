#!/bin/sh
set -e

HOST_ADDRESS="http://localhost:7200"
REPO_NAME="loci-cache"
SPARQL_ENDPOINT="$HOST_ADDRESS/repositories/$REPO_NAME"
STATEMENTS_ENDPOINT="$SPARQL_ENDPOINT/statements"

# Check for dependant env variables.
[ -z "${APP_HOME}" ] && echo "APP_HOME not set" && exit 1
[ -z "${GRAPHDB_HOME}" ] && echo "GRAPHDB_HOME not set" && exit 1
[ -z "${GRAPHDB_SOURCE}" ] && echo "GRAPHDB_SOURCE not set" && exit 1
[ -z "${REPO_CONFIG}" ] && echo "REPO_CONFIG not set" && exit 1

env

echo "GDB_HEAP_SIZE set at ${GDB_HEAP_SIZE}"

if [ -z "$(ls -A $GRAPHDB_SOURCE)" ] || [ -n "${FORCE_REFRESH}" ]; then
    echo "Downloading the Data"
    cd ${GRAPHDB_SOURCE}
    #clear out the old stuff
    echo "Wiping the directory of files at: ${GRAPHDB_SOURCE}"
    rm -rf ${GRAPHDB_SOURCE}/*

    #Download all relevant data
    ${APP_HOME}/download-data.sh    

    #Load all the data into the database (force replace)
    ${GRAPHDB_HOME}/bin/loadrdf -f -m parallel -c ${REPO_CONFIG} ${GRAPHDB_SOURCE}

    #start the db in the background
    ${GRAPHDB_HOME}/bin/graphdb & 

    #wait for it to startup
    echo "Waiting for GraphDB to start up"
    until $(curl --output /dev/null --silent --head --fail http://localhost:7200); do
        printf '.'
        sleep 2
    done
    echo "GraphDB started"

    #Loop precondition file and send to graphql
    for filename in ${APP_HOME}/pre-condition-files/*.sparql; do
        curl -X POST ${STATEMENTS_ENDPOINT} -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: application/sparql-results+json" --data-urlencode "update@$filename"
    done

    unset FORCE_REFRESH

    echo "Wait now for GraphDB to exit"
    wait
else
    #Just start of the GraphDB instance
    echo "Starting GraphsDB with existing data: no building"
    ${GRAPHDB_HOME}/bin/graphdb
fi

