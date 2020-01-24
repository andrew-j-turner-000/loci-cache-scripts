#!/bin/sh
set -e

S3_BASE="https://${S3_BUCKET}.s3-ap-southeast-2.amazonaws.com"
LINKSET_BASE="${S3_BASE}${S3_LINKSET_PATH}"
MANUAL_LINKSET_BASE="${S3_BASE}${S3_MANUAL_LINKSET_PATH}"
DATASET_BASE="${S3_BASE}${S3_DATASET_PATH}"

#Linksets
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/ls_mb16cc.ttl"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_ls_mb16cc.ttl"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/ls_addrcatch.trig"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/ls_addr201605catch.ttl"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_ls_addr201605catch.ttl"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/ls_addr1605mb16.ttl"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_ls_addr1605mb16.ttl"

# wget "${MANUAL_LINKSET_BASE}/${ADDR16052MB11_LINKSET_FILE}"

#mb11mb16
#addrcatch-linkset
#addrmb11-linkset
#addrmb16-linkset
#addr1605mb11-linkset
#addr1605mb16-linkset

#Datasets and Register Info
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/asgs2016.ttl"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_asgs2016.trig"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/asgs2016.reg.ttl" -O asgs2016.reg.ttl

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/geofabric2.ttl"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/geofabric.reg.ttl" -O geofabric.reg.ttl
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_geofabric2.trig"

#wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf_current.ttl"
# wget "http://linked.data.gov.au/dataset/gnaf/?_view=reg&_format=text/turtle" -O gnafCurrent.reg.ttl

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf_201605_addressSites_instances.nt.gz"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_gnaf_201605_addressSites_instances.nt"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf_201605_address_instances.nt.gz"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf_201605_locality_instances.nt.gz"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_gnaf_201605_locality_instances.nt"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf_201605_streetLocality_instances.nt.gz"
wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/trips_plus_gnaf_201605_streetLocality_instances.nt"

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf201605.reg.ttl" -O gnaf201605.reg.ttl


#Externally published Ontologies
wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/asgs.ont.ttl -O asgs.ont.ttl

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/gnaf.ont.ttl -O gnaf.ont.ttl

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/geofabric.ont.ttl -O geofabric.ont.ttl

wget "https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/hy_features.ont.ttl" -O hy_features.ont.ttl

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/SCHEMA_QUDT-v2.1.ont.ttl -O SCHEMA_QUDT-v2.1.ont.ttl

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/org.ont.ttl -O org.ont.ttl

wget --header="Accept: text/turtle" http://rdfs.org/ns/void -O void.ont.ttl

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/prov-o.ont.ttl -O prov-o.ont.ttl

wget --header="Accept: application/rdf+xml" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/geo.ont.rdf -O geo.ont.rdf

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/registry.ont.ttl -O registry.ont.ttl

#Local ontologies

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/loci.ont.ttl -O loci.ont.ttl

wget --header="Accept: text/turtle" https://ga-loci-neptune-test.s3-ap-southeast-2.amazonaws.com/geox.ont.ttl -O geox.ont.ttl


if ls *.html 1> /dev/null 2>&1; then
    echo "Likely and error in the downloads, check the URLs"
    exit 1
fi
