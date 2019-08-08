import zipfile
import os
import subprocess
from subprocess import CalledProcessError
import logging
import boto3
from botocore import UNSIGNED
from botocore.client import Config

logging.basicConfig(level=logging.DEBUG)

def run_command(command_line_array):
    output = ''
    output = subprocess.check_output(command_line_array, universal_newlines=True)
    logging.info(output)

def prepare_database():
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-c", "DROP DATABASE IF EXISTS mydb;"])
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-c", "CREATE DATABASE mydb;"])
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-d", "mydb", 
    "-c", "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"])

def load_asgs_mb():
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

def get_geofabric_assets():
    if not os.path.exists('../assets'):
        os.makedirs('../assets')
    if not os.path.exists('../assets/HR_Catchments_GDB_V2_1_1.zip'):
        run_command(['aws', 's3', 'cp', 's3://loci-assets/source-data/geofabric_2-1/HR_Catchments_GDB_V2_1_1.zip', '../assets/', '--no-sign-request'])
        with zipfile.ZipFile('../assets/HR_Catchments_GDB_V2_1_1.zip', 'r') as zip_ref:
            zip_ref.extractall('../assets')

def load_geofabric_catchments():
    '''
    Note: No need to set -nlt MULTIPOLYGON here, because the .gdb file already defines the shapes as MULTIPOLYGON.
    All Geofabric cooards are in crs EPSG:4326 (WGS-84), but the geometry column in the catchments table DOES NOT contain a SRID declaration, so you need to add it yourself in the query
    eg: ST_GeomFromWKB(wkb_geometry, 4326). Then we need to convert it to albers (EPSG:3577) in order to do constant-area intersections with meshblocks.
    '''
    run_command(["ogr2ogr", "-f", "PostgreSQL", "PG:host=postgis port=5432 dbname=mydb user=postgres password=password", 
        "../assets/HR_Catchments_GDB/HR_Catchments.gdb", "-skipfailures", "-overwrite", "-progress", "--config", "PG_USE_COPY", "YES"])

prepare_database()
load_asgs_mb()
get_geofabric_assets()
load_geofabric_catchments()