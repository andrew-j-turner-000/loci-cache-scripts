
On start, the container will check for the presence of files in the `GRAPHDBSOURCE` directory. If found, it will assume data has been already loaded and simply start the database.
If no files are found, it will completely refresh the cache.

> docker-compose up -d


# Build Env Variables
`GRAPHDBSOURCE` is the location of downloaded files, by default `/app/cachedata`

# Run Env Variables
You only want to set these variables as sort of command line arguments when running the container. If you set at build time, every time
container run from new, they will be used, and for thing like force_refresh, that would be annoying.
`FORCE_REFRESH` if set, will force the refresh of data, deleting all files in `GRAPHDBSOURCE`, and a reload of the database repository
To use refresh, do something like `docker-compose run -e FORCE_REFRESH=true graphcache`

# Volumes
Its probably a good idea to create volumes for both the GraphDB backend, and `GRAPHDBSOURCE` directory so the containers don't do a full reload everytime they start up.

-v /host/datadir:/app/cachedata
-v /host/graphdbdata:/graphdb/data

