import linksets_builder
import utils
import logging
logging.basicConfig(level=logging.DEBUG)

s3_geofabric_rr_path = utils.fail_or_getenv('S3_GEOFABRIC_RR_PATH')

def get_riverregion_assets():
    logging.info("Downloading geofabric riverregion spatial data")
    linksets_builder.get_s3_assets('HR_Regions_GDB_V2_1_1', linksets_builder.s3_bucket, linksets_builder.s3_source_data_path + s3_geofabric_rr_path)

def load_geofabric_riverregions():
    '''
    Loads Geofabric river regions into PostGIS
    '''
    logging.info("Loading geofabric River Regions")

    linksets_builder.load_via_ogr("../assets/HR_Regions_GDB/HR_Regions.gdb", "from", source_data_table="RiverRegion", define_target_geometry_type=None)
    utils.alter_column_name("from", "hydroid", "hydroid_rr")
    utils.buffer_geometry("from", "geom_3577", 10)
    from_id_column = "hydroid_rr"
    return from_id_column

if __name__ == "__main__":
    #Generic preparation logic
    linksets_builder.prepare_database()

    #Specific meshblock and catchment logic TODO: This and generic logic will be seperated further in future refactors
    linksets_builder.get_geofabric_assets()
    get_riverregion_assets()
    load_from_data = load_geofabric_riverregions
    load_to_data = linksets_builder.load_geofabric_catchments
    from_id_column = load_from_data()
    to_id_column = load_to_data()

    # Generic linksets builder logic
    linksets_builder.build_linkset(from_id_column, to_id_column)