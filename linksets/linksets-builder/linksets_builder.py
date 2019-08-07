import subprocess
from subprocess import CalledProcessError
import logging
logging.basicConfig(level=logging.DEBUG)

def run_command(command_line_array):
    output = ''
    try: 
        output = subprocess.check_output(command_line_array, universal_newlines=True)
    except CalledProcessError as e:
        logging.error(e.output)
    logging.info(output)

run_command(["psql", "--host", "postgis", "--user", "postgres", "-c", "DROP DATABASE IF EXISTS mydb;"])
run_command(["psql", "--host", "postgis", "--user", "postgres", "-c", "CREATE DATABASE mydb;"])
run_command(["psql", "--host", "postgis", "--user", "postgres", "-d", "mydb", 
"-c", "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"])

'''
Load ASGS Mesh Blocks into PostGIS
Note: `-nlt MULTIPOLYGON` is specified here, because by default it will ingest as MULTISURFACE, which doesn't work well for our use-case.
There will be some errors when it tries to import mb:mb_pt, because it POINTS don't work with MULTIPOLYGON layer types. Ignore this. We don't use mb_pt
All ASGS coords are in crs EPSG:3857, this needs to be transformed to albers (EPSG:3577) in the sql query in order to do constant-area intersections with catchments 
eg: ST_Transform(wkb_geometry, 3577)
'''
run_command(["ogr2ogr", "-f", "PostgreSQL", "PG:host=postgis port=5432 dbname=mydb user=postgres password=password", 
    "WFS:https://geo.abs.gov.au/arcgis/services/ASGS2016/MB/MapServer/WFSServer", "-skipfailures", "-overwrite", "-progress", "-nlt",
    "MULTIPOLYGON", "--config", "PG_USE_COPY", "YES"])