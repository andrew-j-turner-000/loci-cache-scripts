
On start, the container will check for the presence of files in the `GRAPHDBSOURCE` directory. If found, it will assume data has been already loaded and simply start the database.
If no files are found, it will completely refresh the cache.


# Env Variables
`GRAPHDBSOURCE` is the location of downloaded files, by default `/app/cachedata`
`FORCE_REFRESH` if set, will force the refresh of data, deleting all files in `GRAPHDBSOURCE`, and a reload of the database repository

# Volumes
Its probably a good idea to create volumes for both the GraphDB backend, and `GRAPHDBSOURCE` directory so the containers don't do a full reload everytime they start up.

-v /host/datadir:/app/cachedata
-v /host/graphdbdata:/graphdb/data

