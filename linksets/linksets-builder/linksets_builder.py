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
    '''
    Utility for running commands and logging outputs
    '''
    output = ''
    output = subprocess.check_output(command_line_array, universal_newlines=True)
    logging.info(output)

def prepare_database():
    '''
    Create and prepare a postgis database for geospatial processing
    '''
    logging.info("Preparing Database")
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
    eg: ST_Transform(shape, 3577)
    '''
    logging.info("Loading asgs meshblocks")
    run_command(["ogr2ogr", "-f", "PostgreSQL", "PG:host=postgis port=5432 dbname=mydb user=postgres password=password", 
        "WFS:https://geo.abs.gov.au/arcgis/services/ASGS2016/MB/MapServer/WFSServer", "-skipfailures", "-overwrite", "-progress", "-nlt",
        "MULTIPOLYGON", "--config", "PG_USE_COPY", "YES"])

def get_geofabric_assets():
    logging.info("Downloading geofabric spatial data")
    if not os.path.exists('../assets'):
        os.makedirs('../assets')
    if not os.path.exists('../assets/HR_Catchments_GDB_V2_1_1.zip'):
        run_command(['aws', 's3', 'cp', 's3://loci-assets/source-data/geofabric_2-1/HR_Catchments_GDB_V2_1_1.zip', '../assets/', '--no-sign-request'])
        with zipfile.ZipFile('../assets/HR_Catchments_GDB_V2_1_1.zip', 'r') as zip_ref:
            zip_ref.extractall('../assets')

def load_geofabric_catchments():
    '''
    Loads Geofabric Catchments into PostGIS
    Note: No need to set -nlt MULTIPOLYGON here, because the .gdb file already defines the shapes as MULTIPOLYGON.
    All Geofabric cooards are in crs EPSG:4326 (WGS-84), but the geometry column in the catchments table DOES NOT contain a SRID declaration, so you need to add it yourself in the query
    eg: ST_GeomFromWKB(shape, 4326). Then we need to convert it to albers (EPSG:3577) in order to do constant-area intersections with meshblocks.
    '''
    logging.info("Loading geofabric catchments")
    run_command(["ogr2ogr", "-f", "PostgreSQL", "PG:host=postgis port=5432 dbname=mydb user=postgres password=password", 
        "../assets/HR_Catchments_GDB/HR_Catchments.gdb", "-skipfailures", "-overwrite", "-progress", "--config", "PG_USE_COPY", "YES"])


def harmonize_crs_albers():
    '''
    Harmonize CRS to albers (EPSG:3577) in otder to do constant-area intersections with meshblocks
    '''
    logging.info("Harmonizing coordinates to the albers reference system")
    harmonize_crs_sql = """
    ALTER TABLE public.\"mb:mb\" ADD COLUMN geom_3577 (Geometry,3577);
    UPDATE public.\"mb:mb\" SET geom_3577 = ST_MakeValid(ST_Transform(shape,3577));
    ALTER TABLE public.\"ahgfcontractedcatchment\" ADD COLUMN geom_3577 geometry(Geometry,3577);
    UPDATE public.\"ahgfcontractedcatchment\" SET geom_3577 = ST_Transform(ST_MakeValid(ST_GeomFromEWKB(shape, 4326)),3577);
    """
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-d", "mydb", "-c", harmonize_crs_sql])


def create_geometry_indexes():
    '''
    Create indexes on geometry columns for performance
    '''
    logging.info("Creating Geometry Indexes")
    create_geometry_indexes_sql = """
    CREATE INDEX mb_geom_3577_gix ON public.\"mb:mb\" USING GIST (geom_3577);
    CREATE INDEX cc_geom_3577_gix ON public.\"ahgfcontractedcatchment\" USING GIST (geom_3577);
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_geometry_indexes_sql])

def create_intersections():
    logging.info("Calculating intersecting mb and cc")
    create_intersection_sql = """
CREATE MATERIALIZED VIEW mbintersectcc_mv AS
SELECT mb.mb_code_2016, ca.hydroid, ST_Intersection(mb.geom_3577, ca.geom_3577) as i
FROM public.\"ahgfcontractedcatchment\" as ca
INNER JOIN public.\"mb:mb\" as mb ON mb.geom_3577 && ca.geom_3577 -- the && specifies an indexed bounding box lookup
WHERE ST_IsValid(ca.geom_3577) AND ST_IsValid(mb.geom_3577) AND ST_Intersects(mb.geom_3577, ca.geom_3577)
ORDER BY mb.mb_code_2016 ASC;
CREATE MATERIALIZED VIEW ccintersectmb_mv AS
SELECT ca.hydroid, mb.mb_code_2016, ST_Intersection(ca.geom_3577, mb.geom_3577) as i
FROM public.\"mb:mb\" as mb
INNER JOIN public.\"ahgfcontractedcatchment\" as ca ON ca.geom_3577 && mb.geom_3577 -- the && specifies an indexed bounding box lookup
WHERE ST_IsValid(ca.geom_3577) AND ST_IsValid(mb.geom_3577) AND ST_Intersects(ca.geom_3577, mb.geom_3577)
ORDER BY ca.hydroid ASC;
"""
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_intersection_sql])

def create_indexes():
    '''
    Create indexes on geometry columns for performance
    '''
    logging.info("Creating Geometry Indexes")
    create_geometry_indexes_sql = """
    CREATE INDEX mbintersects_mb_code_idx ON public.\"mbintersectccareas\" USING GIST (mb_code_2016);
    CREATE INDEX mbintersects_hydroid_idx ON public.\"ccintersectsmbareas\" USING GIST (hydroid);
    CREATE INDEX _mb_code_idx ON public.\"mbintersectcc_mv\" USING GIST (mb_code_2016);
    CREATE INDEX mbintersects_hydroid_idx ON public.\"mbintersectcc_mv\" USING GIST (hydroid);
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_geometry_indexes_sql])

def create_intersections_areas():
    logging.info("Calculating intersecting area for mb and cc")
    create_intersection_areas_sql = """
CREATE VIEW mbintersectccareas AS
SELECT s.mb_code_2016, s.hydroid, s.mb_area, s.cc_area, s.i_area, (s.i_area / s.mb_area) as mb_proportion, (s.i_area / s.cc_area) as cc_proportion, s.geomcollection FROM (
    SELECT mv.mb_code_2016,
           mv.hydroid,
           ST_Area(mb.geom_3577)                         as mb_area,
           ST_Area(ca.geom_3577)                         as cc_area,
           ST_Area(mv.i)                                 as i_area,
           ST_Collect(ARRAY[ca.geom_3577, mb.geom_3577, mv.i]) as geomcollection
    FROM mbintersectcc_mv as mv
    INNER JOIN public.\"mb:mb\" as mb ON mb.mb_code_2016 = mv.mb_code_2016
    INNER JOIN public.\"ahgfcontractedcatchment\" as ca ON ca.hydroid = mv.hydroid
) as s;
CREATE VIEW ccintersectmbareas AS
SELECT s.hydroid, s.mb_code_2016, s.cc_area, s.mb_area, s.i_area, (s.i_area / s.cc_area) as cc_proportion, (s.i_area / s.mb_area) as mb_proportion, s.geomcollection FROM (
    SELECT mv.hydroid,
           mv.mb_code_2016,
           ST_Area(ca.geom_3577)                         as cc_area,
           ST_Area(mb.geom_3577)                         as mb_area,
           ST_Area(mv.i)                                 as i_area,
           ST_Collect(ARRAY[mb.geom_3577, ca.geom_3577, mv.i]) as geomcollection
    FROM ccintersectmb_mv as mv
    INNER JOIN public.\"ahgfcontractedcatchment\" as ca ON ca.hydroid = mv.hydroid
    INNER JOIN public.\"mb:mb\" as mb ON mb.mb_code_2016 = mv.mb_code_2016
) as s;
"""
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_intersection_areas_sql])

def find_bad_meshblocks():
    logging.info("Finding bad meshblocks (unused at the moment)")
    '''
    Find bad mesblocks
    Meshblocks smaller than an specified area and meshblock proportion (is that amount in the meshblock when it intersects?)
    is larger than a small ratio
    or 
    Mesblocks where intersecting area smaller than a specified area 
    and catchment proportion (maybe the amount intersecting that is in the catchment) is larger than a small ratio 
    '''
    find_bad_meshblocks_sql = """
    CREATE MATERIALIZED VIEW bad_meshblocks as
    SELECT mb.mb_code_2016, mb.hydroid FROM mbintersectccareas as mb
    WHERE mb.mb_area < 1100.0 and ((mb_proportion >= 0.010)or(cc_proportion >= 0.010)) and i_area <= 50.0;
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", find_bad_meshblocks_sql])

def create_classifier_views():
    logging.info("Classifying ambiguous overlapping meshblocks thresholds")
    '''
    annotate meshblocks and cc to indicate whether they are considered truely overlapping or close enough to be within
    when they intersect 
    '''
    create_classifier_views_sql = """
    CREATE VIEW mbintersectccareas_classify AS
    SELECT mb.*, mb_proportion >= 0.010 as is_overlaps, mb_proportion >=0.990 as is_within
    FROM mbintersectccareas as mb;
    -- (TODO: minus bad meshblocks)
    CREATE VIEW ccintersectmbareas_classify AS
    SELECT cc.*, cc_proportion >= 0.010 as is_overlaps, cc_proportion >=0.990 as is_within
    FROM ccintersectmbareas as cc;
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_classifier_views_sql])

#prepare_database()
#load_asgs_mb()
#get_geofabric_assets()
#load_geofabric_catchments()
#harmonize_crs_albers()
#create_geometry_indexes()
create_intersections()
create_intersections_areas()
find_bad_meshblocks()
create_classifier_views()