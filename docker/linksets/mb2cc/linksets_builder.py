import zipfile
import os
import logging
import utils
from utils import run_command
logging.basicConfig(level=logging.DEBUG)

LIMIT_LOAD = utils.fail_or_getenv('LIMIT_LOAD', warn_only=True)
s3_bucket = utils.fail_or_getenv('S3_BUCKET')
s3_source_data_path = utils.fail_or_getenv('S3_SOURCE_DATA_PATH')
s3_geofabric_path = utils.fail_or_getenv('S3_GEOFABRIC_PATH')
s3_asgs_2016_mb_path = utils.fail_or_getenv('S3_ASGS_2016_MB_PATH')
asgs_mb_wfs_url = utils.fail_or_getenv('ASGS_MB_WFS_URL')
# check that AWS keys are defined for command line aws s3 calls
utils.fail_or_getenv('AWS_ACCESS_KEY_ID')
utils.fail_or_getenv('AWS_SECRET_ACCESS_KEY')
asgs_2016_local_name_prefix = "mb_2016_all_shape"


def load_via_ogr(source_data, target_table_name, source_data_table=None, define_target_geometry_type='MULTIPOLYGON', limit=LIMIT_LOAD):
    '''
    Loads spatial data into postgis
    :param source_data: source data for ogr2ogr to load into postgres
    :param define_target_geometry_type: target geometry type see ogr2ogr documentation, defaults to MULTIPOLYGON
    :param limit: limit the number of rows loaded, used for testing, defaults to None which is no limit
    '''
    limit_args = []
    if limit is not None:
        limit_args = ["-limit", limit]

    target_geometry_args = []
    if define_target_geometry_type is not None:
        target_geometry_args = ["-nlt", define_target_geometry_type]

    source_data_table_args = []
    if source_data_table is not None:
        source_data_table_args = [source_data_table]

    run_command(["ogr2ogr", "-f", "PostgreSQL", "PG:host=postgis port=5432 dbname=mydb user=postgres password=password",
                source_data, "-skipfailures", "-overwrite", "-progress", "-nln", target_table_name] + source_data_table_args + ["-lco", "GEOMETRY_NAME=geom_3577", "-lco", "PRECISION=NO", "-t_srs", "EPSG:3577"] + target_geometry_args + limit_args + ["--config", "PG_USE_COPY", "YES"])


def prepare_database():
    '''
    Create and prepare a postgis database for geospatial processing
    '''
    logging.info("Preparing Database")
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-c", "DROP DATABASE IF EXISTS mydb;"])
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-c", "CREATE DATABASE mydb;"])
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-d", "mydb", 
                "-c", "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"])


def get_s3_assets(local_file_name_save_to, s3_bucket, s3_path):
    '''
    Download zipped s3 assets and unzip them 
    '''
    if not os.path.exists('../assets'):
        os.makedirs('../assets')
    run_command(['aws', 's3', 'cp', 's3://{}{}'.format(s3_bucket, s3_path), '../assets/'])
    with zipfile.ZipFile('../assets/{}.zip'.format(local_file_name_save_to), 'r') as zip_ref:
        zip_ref.extractall('../assets')


def get_geofabric_assets():
    logging.info("Downloading geofabric spatial data")
    get_s3_assets('HR_Catchments_GDB_V2_1_1', s3_bucket, s3_source_data_path + s3_geofabric_path)


def get_meshblock_assets():
    logging.info("Downloading asgs 2016 spatial data")
    get_s3_assets(asgs_2016_local_name_prefix, s3_bucket, s3_source_data_path + s3_asgs_2016_mb_path)


def load_geofabric_catchments():
    '''
    Loads Geofabric Catchments into PostGIS
    Note: No need to set -nlt MULTIPOLYGON here, because the .gdb file already defines the shapes as MULTIPOLYGON.
    All Geofabric cooards are in crs EPSG:4326 (WGS-84), but the geometry column in the catchments table DOES NOT contain a SRID declaration, so you need to add it yourself in the query
    eg: ST_GeomFromWKB(shape, 4326). Then we need to convert it to albers (EPSG:3577) in order to do constant-area intersections with meshblocks.
    '''
    logging.info("Loading geofabric catchments")
    load_via_ogr("../assets/HR_Catchments_GDB/HR_Catchments.gdb", "to", source_data_table="AHGFContractedCatchment", define_target_geometry_type=None)
    to_id_column = "hydroid"
    return to_id_column


def load_asgs_mb():
    '''
    Load ASGS Mesh Blocks into PostGIS
    Note: `-nlt MULTIPOLYGON` is specified here, because by default it will ingest as MULTISURFACE, which doesn't work well for our use-case.
    There will be some errors when it tries to import from_pt, because it POINTS don't work with MULTIPOLYGON layer types. Ignore this. We don't use mb_pt
    All ASGS coords are in crs EPSG:3857, this needs to be transformed to albers (EPSG:3577) in the sql query in order to do constant-area intersections with catchments 
    eg: ST_Transform(shape, 3577)
    '''
    logging.info("Loading asgs meshblocks")
    load_via_ogr("../assets/{}/MB_MB.shp".format(asgs_2016_local_name_prefix), "from")
    from_id_column = "mb_code_20"
    return from_id_column 

def fix_geometries():
    '''
    makes valid any invalid geometries in the from and to tables
    '''
    utils.geometry_fix("from", "geom_3577")
    utils.geometry_fix("to", "geom_3577")

def create_geometry_indexes():
    '''
    Create indexes on geometry columns for performance
    '''
    logging.info("Creating Geometry Indexes")
    create_geometry_indexes_sql = """
    CREATE INDEX from_geom_3577_gix ON public.\"from\" USING GIST (geom_3577);
    CREATE INDEX to_geom_3577_gix ON public.\"to\" USING GIST (geom_3577);
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_geometry_indexes_sql])


def create_intersections(from_id_column, to_id_column):
    """
    Intersects from and to tables 
    :param from_id_column: name of a column containing a unique key in the from geospatial table it will be used for suffixing identifiers later 
    :param to_id_column: name of a column containing a unique key in the to geospatial table it will be used for suffixing identifiers later 
    """
    logging.info("Calculating intersecting from and to")
    create_intersection_sql = """
    CREATE MATERIALIZED VIEW fromintersectto_mv AS
    SELECT from_t.\"{from_id_column}\", to_t.\"{to_id_column}\", ST_Intersection(from_t.geom_3577, to_t.geom_3577) as i
    FROM public.\"to\" as to_t 
    INNER JOIN public.\"from\" as from_t ON from_t.geom_3577 && to_t.geom_3577 -- the && specifies an indexed bounding box lookup
    WHERE ST_IsValid(to_t.geom_3577) AND ST_IsValid(from_t.geom_3577) AND ST_Intersects(from_t.geom_3577, to_t.geom_3577)
    ORDER BY from_t.\"{from_id_column}\" ASC;
    CREATE MATERIALIZED VIEW tointersectfrom_mv AS
    SELECT to_t.\"{to_id_column}\", from_t.\"{from_id_column}\", ST_Intersection(to_t.geom_3577, from_t.geom_3577) as i
    FROM public.\"from\" as from_t
    INNER JOIN public.\"to\" as to_t ON to_t.geom_3577 && from_t.geom_3577 -- the && specifies an indexed bounding box lookup
    WHERE ST_IsValid(to_t.geom_3577) AND ST_IsValid(from_t.geom_3577) AND ST_Intersects(to_t.geom_3577, from_t.geom_3577)
    ORDER BY to_t.\"{to_id_column}\" ASC;
    """.format(from_id_column=from_id_column, to_id_column=to_id_column)
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_intersection_sql])



def create_intersections_areas(from_id_column, to_id_column):
    """
    Calculates intersecting areas
    :param from_id_column: name of a column containing a unique key in the from geospatial table it will be used for suffixing identifiers later 
    :param to_id_column: name of a column containing a unique key in the to geospatial table it will be used for suffixing identifiers later 
    """
    logging.info("Calculating intersecting area for from and to")
    create_intersection_areas_sql = """
    CREATE VIEW fromintersecttoareas AS
    SELECT s.\"{from_id_column}\", s.\"{to_id_column}\", s.from_area, s.to_area, s.i_area, (s.i_area / s.from_area) as from_proportion, (s.i_area / s.to_area) as to_proportion, s.geomcollection FROM (
    SELECT mv.\"{from_id_column}\",
           mv.\"{to_id_column}\",
           ST_Area(from_t.geom_3577)                         as from_area,
           ST_Area(to_t.geom_3577)                         as to_area,
           ST_Area(mv.i)                                 as i_area,
           ST_Collect(ARRAY[to_t.geom_3577, from_t.geom_3577, mv.i]) as geomcollection
    FROM fromintersectto_mv as mv
    INNER JOIN public.\"from\" as from_t ON from_t.\"{from_id_column}\" = mv.\"{from_id_column}\"
    INNER JOIN public.\"to\" as to_t ON to_t.\"{to_id_column}\" = mv.\"{to_id_column}\"
    ) as s;
    CREATE VIEW tointersectfromareas AS
    SELECT s.\"{to_id_column}\", s.\"{from_id_column}\", s.to_area, s.from_area, s.i_area, (s.i_area / s.to_area) as to_proportion, (s.i_area / s.from_area) as from_proportion, s.geomcollection FROM (
    SELECT mv.\"{to_id_column}\",
           mv.\"{from_id_column}\",
           ST_Area(to_t.geom_3577)                         as to_area,
           ST_Area(from_t.geom_3577)                         as from_area,
           ST_Area(mv.i)                                 as i_area,
           ST_Collect(ARRAY[from_t.geom_3577, to_t.geom_3577, mv.i]) as geomcollection
    FROM tointersectfrom_mv as mv
    INNER JOIN public.\"to\" as to_t ON to_t.\"{to_id_column}\" = mv.\"{to_id_column}\"
    INNER JOIN public.\"from\" as from_t ON from_t.\"{from_id_column}\" = mv.\"{from_id_column}\"
    ) as s;
    """.format(from_id_column=from_id_column, to_id_column=to_id_column)
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_intersection_areas_sql])
#

def create_classifier_views():
    '''
    annotate from and to, to indicate whether they are considered truely overlapping or close enough to be within
    when they intersect 
    '''
    logging.info("Classifying ambiguous overlapping meshblocks thresholds")
    create_classifier_views_sql = """
    CREATE VIEW fromintersecttoareas_classify AS
    SELECT from_t.*, from_t.from_proportion >= 0.010 as is_overlaps, from_t.from_proportion >=0.990 as is_within
    FROM fromintersecttoareas as from_t;
    CREATE VIEW tointersectfromareas_classify AS
    SELECT to_t.*, to_t.to_proportion >= 0.010 as is_overlaps, to_t.to_proportion >=0.990 as is_within
    FROM tointersectfromareas as to_t;
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_classifier_views_sql])

def build_linkset(from_id_column, to_id_column):
    fix_geometries()
    create_geometry_indexes()
    create_intersections(from_id_column, to_id_column)
    create_intersections_areas(from_id_column, to_id_column)
    create_classifier_views()

if __name__ == "__main__":
    #Generic preparation logic
    prepare_database()

    #Specific meshblock and catchment logic TODO: This and generic logic will be seperated further in future refactors
    get_geofabric_assets()
    get_meshblock_assets()
    load_from_data = load_asgs_mb
    load_to_data = load_geofabric_catchments
    from_id_column = load_from_data()
    to_id_column = load_to_data()

    # Generic linksets builder logic
    build_linkset(from_id_column, to_id_column)
