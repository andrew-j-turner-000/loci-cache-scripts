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
asgs_2016_local_name_prefix = "mb_2016_all_shape"


def load_via_ogr(source_data, define_target_geometry_type='MULTIPOLYGON', limit=LIMIT_LOAD):
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

    run_command(["ogr2ogr", "-f", "PostgreSQL", "PG:host=postgis port=5432 dbname=mydb user=postgres password=password",
                source_data, "-skipfailures", "-overwrite", "-progress"] + target_geometry_args + limit_args + ["--config", "PG_USE_COPY", "YES"])


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
    There will be some errors when it tries to import mb_mb_pt, because it POINTS don't work with MULTIPOLYGON layer types. Ignore this. We don't use mb_pt
    All ASGS coords are in crs EPSG:3857, this needs to be transformed to albers (EPSG:3577) in the sql query in order to do constant-area intersections with catchments 
    eg: ST_Transform(shape, 3577)
    '''
    logging.info("Loading asgs meshblocks")
    load_via_ogr("../assets/{}/MB_MB.shp".format(asgs_2016_local_name_prefix))


def get_s3_assets(local_file_name_save_to, s3_bucket, s3_path):
    '''
    Download zipped s3 assets and unzip them 
    '''
    if not os.path.exists('../assets'):
        os.makedirs('../assets')
    if not os.path.exists('../assets/{}'.format(local_file_name_save_to)):
        run_command(['aws', 's3', 'cp', 's3://{}{}'.format(s3_bucket, s3_path), '../assets/', '--no-sign-request'])
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
    load_via_ogr("../assets/HR_Catchments_GDB/HR_Catchments.gdb", define_target_geometry_type=None)


def harmonize_crs_albers():
    '''
    Harmonize CRS to albers (EPSG:3577) in otder to do constant-area intersections with meshblocks
    '''
    logging.info("Harmonizing coordinates to the albers reference system")
    harmonize_crs_sql = """
    ALTER TABLE public.\"mb_mb\" ADD COLUMN geom_3577 geometry(Geometry,3577);
    UPDATE public.\"mb_mb\" SET geom_3577 = ST_MakeValid(ST_Transform(wkb_geometry,3577));
    ALTER TABLE public.\"ahgfcontractedcatchment\" ADD COLUMN geom_3577 geometry(Geometry,3577);
    UPDATE public.\"ahgfcontractedcatchment\" SET geom_3577 = ST_Transform(ST_MakeValid(ST_GeomFromEWKB(shape)),3577);
    """
    run_command(["psql", "--host", "postgis", "--user", "postgres", "-d", "mydb", "-c", harmonize_crs_sql])


def create_geometry_indexes():
    '''
    Create indexes on geometry columns for performance
    '''
    logging.info("Creating Geometry Indexes")
    create_geometry_indexes_sql = """
    CREATE INDEX mb_geom_3577_gix ON public.\"mb_mb\" USING GIST (geom_3577);
    CREATE INDEX cc_geom_3577_gix ON public.\"ahgfcontractedcatchment\" USING GIST (geom_3577);
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_geometry_indexes_sql])


def create_intersections():
    logging.info("Calculating intersecting mb and cc")
    create_intersection_sql = """
    CREATE MATERIALIZED VIEW mbintersectcc_mv AS
    SELECT mb.mb_code_20, ca.hydroid, ST_Intersection(mb.geom_3577, ca.geom_3577) as i
    FROM public.\"ahgfcontractedcatchment\" as ca
    INNER JOIN public.\"mb_mb\" as mb ON mb.geom_3577 && ca.geom_3577 -- the && specifies an indexed bounding box lookup
    WHERE ST_IsValid(ca.geom_3577) AND ST_IsValid(mb.geom_3577) AND ST_Intersects(mb.geom_3577, ca.geom_3577)
    ORDER BY mb.mb_code_20 ASC;
    CREATE MATERIALIZED VIEW ccintersectmb_mv AS
    SELECT ca.hydroid, mb.mb_code_20, ST_Intersection(ca.geom_3577, mb.geom_3577) as i
    FROM public.\"mb_mb\" as mb
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
    CREATE INDEX mbintersects_mb_code_idx ON public.\"mbintersectccareas\" USING GIST (mb_code_20);
    CREATE INDEX mbintersects_hydroid_idx ON public.\"ccintersectsmbareas\" USING GIST (hydroid);
    CREATE INDEX _mb_code_idx ON public.\"mbintersectcc_mv\" USING GIST (mb_code_20);
    CREATE INDEX mbintersects_hydroid_idx ON public.\"mbintersectcc_mv\" USING GIST (hydroid);
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_geometry_indexes_sql])


def create_intersections_areas():
    logging.info("Calculating intersecting area for mb and cc")
    create_intersection_areas_sql = """
    CREATE VIEW mbintersectccareas AS
    SELECT s.mb_code_20, s.hydroid, s.mb_area, s.cc_area, s.i_area, (s.i_area / s.mb_area) as mb_proportion, (s.i_area / s.cc_area) as cc_proportion, s.geomcollection FROM (
    SELECT mv.mb_code_20,
           mv.hydroid,
           ST_Area(mb.geom_3577)                         as mb_area,
           ST_Area(ca.geom_3577)                         as cc_area,
           ST_Area(mv.i)                                 as i_area,
           ST_Collect(ARRAY[ca.geom_3577, mb.geom_3577, mv.i]) as geomcollection
    FROM mbintersectcc_mv as mv
    INNER JOIN public.\"mb_mb\" as mb ON mb.mb_code_20 = mv.mb_code_20
    INNER JOIN public.\"ahgfcontractedcatchment\" as ca ON ca.hydroid = mv.hydroid
    ) as s;
    CREATE VIEW ccintersectmbareas AS
    SELECT s.hydroid, s.mb_code_20, s.cc_area, s.mb_area, s.i_area, (s.i_area / s.cc_area) as cc_proportion, (s.i_area / s.mb_area) as mb_proportion, s.geomcollection FROM (
    SELECT mv.hydroid,
           mv.mb_code_20,
           ST_Area(ca.geom_3577)                         as cc_area,
           ST_Area(mb.geom_3577)                         as mb_area,
           ST_Area(mv.i)                                 as i_area,
           ST_Collect(ARRAY[mb.geom_3577, ca.geom_3577, mv.i]) as geomcollection
    FROM ccintersectmb_mv as mv
    INNER JOIN public.\"ahgfcontractedcatchment\" as ca ON ca.hydroid = mv.hydroid
    INNER JOIN public.\"mb_mb\" as mb ON mb.mb_code_20 = mv.mb_code_20
    ) as s;
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_intersection_areas_sql])


def find_bad_meshblocks():
    '''
    Find bad mesblocks
    Meshblocks smaller than an specified area and meshblock proportion (is that amount in the meshblock when it intersects?)
    is larger than a small ratio
    or 
    Mesblocks where intersecting area smaller than a specified area 
    and catchment proportion (maybe the amount intersecting that is in the catchment) is larger than a small ratio 
    '''
    logging.info("Finding bad meshblocks (unused at the moment)")
    find_bad_meshblocks_sql = """
    CREATE MATERIALIZED VIEW bad_meshblocks as
    SELECT mb.mb_code_20, mb.hydroid FROM mbintersectccareas as mb
    WHERE mb.mb_area < 1100.0 and ((mb_proportion >= 0.010)or(cc_proportion >= 0.010)) and i_area <= 50.0;
    """
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", find_bad_meshblocks_sql])

def create_classifier_views():
    '''
    annotate meshblocks and cc to indicate whether they are considered truely overlapping or close enough to be within
    when they intersect 
    '''
    logging.info("Classifying ambiguous overlapping meshblocks thresholds")
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


if __name__ == "__main__":
    prepare_database()
    get_geofabric_assets()
    get_meshblock_assets()
    load_asgs_mb()
    load_geofabric_catchments()
    harmonize_crs_albers()
    create_geometry_indexes()
    create_intersections()
    create_intersections_areas()
    find_bad_meshblocks()
    create_classifier_views()
