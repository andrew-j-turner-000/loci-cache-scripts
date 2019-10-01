import psycopg2 as pg
import os
import utils
from datetime import datetime
import logging
import fileinput
from io import StringIO

logging.basicConfig(level=logging.DEBUG)

header_template = """ 
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix qudt: <http://qudt.org/schema/qudt#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dbp: <http://dbpedia.org/property/> .
@prefix geo: <http://www.opengis.net/ont/geosparql#> .
@prefix gx: <http://linked.data.gov.au/def/geox#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix loci: <http://linked.data.gov.au/def/loci#> .
@prefix : <http://linked.data.gov.au/dataset/mb16cc/statement/> .
@prefix i: <http://purl.org/dc/terms/isPartOf> .
@prefix l: <http://linked.data.gov.au/dataset/mb16cc> .
@prefix from: <{from_prefix}> .
@prefix to: <{to_prefix}> .
@prefix s: <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> .
@prefix p: <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> .
@prefix o: <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> .
@prefix m: <http://linked.data.gov.au/def/loci/hadGenerationMethod> .
@prefix w: <http://www.opengis.net/ont/geosparql#sfWithin> .
@prefix c: <http://www.opengis.net/ont/geosparql#sfContains> .
@prefix ov: <http://www.opengis.net/ont/geosparql#sfOverlaps> .
@prefix tso: <http://linked.data.gov.au/def/geox#transitiveSfOverlap> .
@prefix f: <http://www.opengis.net/ont/geosparql#Feature> .
@prefix dc: <http://www.w3.org/2001/XMLSchema#decimal> .
@prefix am2: <http://linked.data.gov.au/def/geox#hasAreaM2> .
@prefix dv: <http://linked.data.gov.au/def/datatype/value> .
@prefix crs: <http://www.w3.org/ns/qb4st/crs> .
@prefix albers: <http://www.opengis.net/def/crs/EPSG/0/3577> .

l: a loci:Linkset ;
  dct:title "{header_title}" ;
  dct:description \"\"\"{header_description}\"\"\"@en;
  dct:publisher <http://catalogue.linked.data.gov.au/org/O-000886> ;
  dc:publisher "CSIRO" ;
  dcat:contactPoint _:contact ;
  dct:issued "{creation_date}"^^xsd:date ;
  dct:modified "{creation_date}"^^xsd:date ;
  void:subjectsTarget <{subjects_target}> ;
  void:linkPredicate w: , c: , tso: ;
  void:objectsTarget <{subjects_target}> ;
  m: _:linkset_prov_p .

_:linkset_prov_p a prov:Plan ;
    rdfs:label "Spatial Intersection Method" ;
    prov:value <https://github.com/CSIRO-enviro-informatics/loci-cache-scripts/tree/linksets-builder> ;
    rdfs:comment "{provenance_comment}";
    prov:wasAttributedTo _:contact;
    prov:generatedAtTime "{creation_date}"^^xsd:date .

_:contact a vcard:Individual ;
  vcard:fn {contact_name} ;
  vcard:hasEmail {contact_email} .
"""

from_area_template = """\
from:{from_id_column:s} a f: ;
 am2: [ dv: "{from_area_m2:f}"^^dc: ; crs: albers: ] .
"""
to_area_template = """\
to:{to_id_column:s} a f: ;
 am2: [ dv: "{to_area_m2:f}"^^dc: ; crs: albers: ] .
"""
overlaps_template = """\
:i{intersection_iter:d} a f: ;
 am2: [ dv: "{i_area_m2:f}"^^dc: ; crs: albers: ] .
:mo{intersection_iter:d} s: from:{from_id_column:s} ;
 p: c: ;
 o: :i{intersection_iter:d} ;
 i: l: ;
 m: _:linkset_prov_p.
:co{intersection_iter:d} s: to:{to_id_column:s} ;
 p: c: ;
 o: :i{intersection_iter:d} ;
 i: l: ;
 m: _:linkset_prov_p.
:to{intersection_iter:d} s: from:{from_id_column:s} ;
 p: tso: ;
 o: to:{to_id_column:s};
 i: l: ;
 m: _:mb16to_p .
"""
from_sf_within_template = """\
:mw{within_iter:d} s: from:{from_id_column:s} ;
 p: w: ;
 o: to:{to_id_column:s} ;
 i: l: ;
 m: _:mb16to_p .
"""
from_sf_contains_template = """\
:mc{within_iter:d} s: from:{from_id_column:s} ;
 p: c: ;
 o: to:{to_id_column:s} ;
 i: l: ;
 m: _:mb16to_p .
"""

def do_overlaps(from_id_column, to_id_column):
    logging.info("Generating overlaps statements")
    con = pg.connect("host={} port=5432 dbname=mydb user=postgres password=password".format(database_url))
    cur = con.cursor("cur1")
    command = """\
    SELECT from_t.{from_id_column}, to_t.{to_id_column}, from_t.from_area, to_t.to_area, from_t.i_area, from_t.is_overlaps, to_t.is_overlaps, from_t.is_within, to_t.is_within 
    FROM public.\"fromintersecttoareas_classify\" as to_t 
    INNER JOIN public.\"tointersectfromareas_classify\" as from_t on from_t.{from_id_column} = to_t.{from_id_column} and from_t.{to_id_column} = to_t.{to_id_column}
    WHERE (from_t.is_overlaps or to_t.is_overlaps) and (not from_t.is_within) and (not to_t.is_within)
    -- ORDER BY from_t.{from_id_column};
    """.format(from_id_column=from_id_column, to_id_column=to_id_column)
    c = 0
    intersection_iter = 0
    expressed_from_areas = set()
    expressed_to_areas = set()
    file_like = StringIO()
    cur.copy_expert("COPY ({}) TO STDOUT WITH CSV".format(command), file_like, size=32000)
    file_like.seek(0)
    with open("overlaps_all.ttl", "w") as outfile:
        for line in file_like.readlines():
            record = line.split(',')
            intersection_iter += 1
            c += 1
            from_id_column = str(record[0])
            to_id_column = str(record[1])
            from_area_m2 = float(record[2])
            to_area_m2 = float(record[3])
            i_area_m2  = float(record[4])
            from_area_m2 = round((from_area_m2 / 100.0), 7) * 100.0
            to_area_m2 = round((to_area_m2 / 100.0), 7) * 100.0
            i_area_m2  = round((i_area_m2  / 100.0), 7) * 100.0
            if from_id_column not in expressed_from_areas:
                from_area_chunk = from_area_template.format(from_id_column=from_id_column, from_area_m2=from_area_m2)
                outfile.write(from_area_chunk)
                expressed_from_areas.add(from_id_column)
            if to_id_column not in expressed_to_areas:
                to_area_chunk = to_area_template.format(to_id_column=to_id_column, to_area_m2=to_area_m2)
                outfile.write(to_area_chunk)
                expressed_to_areas.add(to_id_column)
            next_chunk = overlaps_template.format(from_id_column=from_id_column, to_id_column=to_id_column, intersection_iter=intersection_iter, i_area_m2=i_area_m2)
            outfile.write(next_chunk)
            
            
def do_withins(from_id_column, to_id_column):
    logging.info("Generating withins statements")
    con = pg.connect("host={} dbname=mydb user=postgres password=password".format(database_url))
    cur = con.cursor("cur2")
    command = """\
    SELECT from_t.{from_id_column}, to_t.{to_id_column}, from_t.is_within, to_t.is_within
    FROM public.\"fromintersecttoareas_classify\" as from_t
    INNER JOIN public.\"tointersectfromareas_classify\" as to_t on from_t.{from_id_column} = to_t.{from_id_column} and from_t.{to_id_column} = to_t.{to_id_column}
    WHERE from_t.is_within or to_t.is_within
    """.format(from_id_column=from_id_column, to_id_column=to_id_column)
    c = 0
    within_iter = 0
    file_like = StringIO()
    cur.copy_expert("COPY ({}) TO STDOUT WITH CSV".format(command), file_like, size=32000)
    file_like.seek(0)
    with open("within_all.ttl", "w") as outfile:
        for line in file_like.readlines():
            record = line.split(',')
            c+=1
            within_iter += 1
            from_id_column = str(record[0])
            to_id_column = str(record[1])
            from_is_within = (str(record[2]).lower().startswith("t")) 
            to_is_within = (str(record[3]).lower().startswith("t")) 
            if from_is_within:
                next_chunk = from_sf_within_template.format(from_id_column=from_id_column, to_id_column=to_id_column, within_iter=within_iter)
            else:
                next_chunk = from_sf_contains_template.format(from_id_column=from_id_column, to_id_column=to_id_column, within_iter=within_iter)
            outfile.write(next_chunk)


def generate_header(header_description, header_title, contact_name, contact_email, from_prefix, to_prefix, subjects_target, objects_target, provenance_comment):
    """
    Genrates the turtle header describing this linkset
    :param header_description: description of the linkset  
    :param header_title: linkset title 
    :param contact_name: contact name 
    :param contact_email: contact email
    :param from_prefix: prefix uris that identifiers will be appended to to create unique uris for from objects 
    :param to_prefix: prefix uris that identifiers will be appended to to create unique uris for to objects 
    :param subjects_target: uri that identifies the dataset that from objects reside in  
    :param objects_target: uri that identifies the dataset that to objects reside in  
    :param provenance_comment: description of the provenance information 
    """
    with open("header.ttl", "w") as outfile:
        header = header_template.format(header_description=header_description, header_title=header_title, contact_name=contact_name, contact_email=contact_email,\
        creation_date=datetime.today().strftime('%Y-%m-%d'), from_prefix=from_prefix, to_prefix=to_prefix, subjects_target=subjects_target, objects_target=objects_target, provenance_comment=provenance_comment)
        outfile.write(header)


def concat_files(output_linkset_file_name):
    """concatenates header within and overlaps statements into output ttl file"
    :param output_linkset_file_name: output file name
    """
    logging.info("Concatenating headers withins overlaps into compiled linkset file")
    with open(output_linkset_file_name, 'w') as fout, fileinput.input(['./header.ttl', './within_all.ttl', './overlaps_all.ttl']) as fin:
        for line in fin:
            fout.write(line)

if __name__ == "__main__":
    database_url = utils.fail_or_getenv('DATABASE_URL')
    contact_name = utils.fail_or_getenv('CONTACT_NAME')
    contact_email = utils.fail_or_getenv('CONTACT_EMAIL')
    header_description = """This LOC-I Project Linkset relates Meshblock individuals in the ASGS LOC-I Dataset to Contracted Catchment individuals in the Geofabric LOC-I Dataset. All Meshblock -> Catchment relations are either transitiveSfOverlap, sfWithin, or sfContains. That is a Meshblock either overlaps or is wholly within the Catchment, or in some cases the Meshblock wholly contains the Catchment.
    The Linkset triples (Meshblock sfWithin Catchment, Meshblock sfContains Catchment, Meshblock transitiveSfOverlap Catchment) are reified so that each triple is contained within an RDF Statement class instance so that the triple is numbered and the method used to generate the triple is given by the loci:hadGenerationMethod.
    The method used for all triples in this Linkset is the same and it is SpatialIntersection which is defined below.
    The triples for the main data in this linkset - the Statements relating Meshblocks to Catchments - are valid RDF in the Turtle syntax but an unusual namespacing arrangement is used so all terms are indicated with as few letters as possible, mostly one letter then colon, e.g. s: for http://www.w3.org/1999/02/22-rdf-syntax-ns#subject, rather than the more common rdf:subject. This is simply to reduce file size.
    """
    header_title = "Meshblocks Contracted Catchments Linkset"
    to_id_column = "hydroid"
    from_id_column = "mb_code_20"
    subjects_target = "http://linked.data.gov.au/dataset/asgs2016"
    objects_target = "http://linked.data.gov.au/dataset/geofabric"
    from_prefix = "http://linked.data.gov.au/dataset/asgs2016/meshblock/"
    to_prefix = "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/"
    provenance_comment = "The method used to classify Meshblock and Contracted Catchment relationships"
    do_withins(from_id_column, to_id_column)
    do_overlaps(from_id_column, to_id_column)
    generate_header(header_description, header_title, contact_name, contact_email, from_prefix, to_prefix, subjects_target, objects_target, provenance_comment)
    concat_files("ls_mb16cc.ttl")