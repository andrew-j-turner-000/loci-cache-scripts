import linksets_triples_builder
import utils

if __name__ == "__main__":
    database_url = utils.fail_or_getenv('DATABASE_URL')
    contact_name = utils.fail_or_getenv('CONTACT_NAME')
    contact_email = utils.fail_or_getenv('CONTACT_EMAIL')
    header_description = """This LOC-I Project Linkset relates River Regions to Contracted Catchments"""
    header_title = "River Regions to Contracted Catchments Linkset"
    to_id_column = "hydroid"
    from_id_column = "hydroid_rr"
    subjects_target = "http://linked.data.gov.au/dataset/geofabric"
    objects_target = "http://linked.data.gov.au/dataset/geofabric"
    from_prefix = "http://linked.data.gov.au/dataset/geofabric/riverregion/"
    to_prefix = "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/"
    provenance_comment = "The method used to classify river region and Contracted Catchment relationships"
    linksets_triples_builder.database_url = database_url
    linksets_triples_builder.do_withins(from_id_column, to_id_column)
    linksets_triples_builder.do_overlaps(from_id_column, to_id_column)
    linksets_triples_builder.generate_header(header_description, header_title, contact_name, contact_email, from_prefix, to_prefix, subjects_target, objects_target, provenance_comment)
    linksets_triples_builder.concat_files("ls_rr16cc.ttl")
