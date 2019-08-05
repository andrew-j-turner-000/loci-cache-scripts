#!/bin/sh

#Linksets
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/linksets/ls_mb16cc.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/linksets/ls_addrcatch.trig

#mb11mb16
#addrcatch-linkset
#addrmb11-linkset
#addrmb16-linkset
#addr1605mb11-linkset
#addr1605mb16-linkset

#Datasets
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/auto-generated/datasets/asgs2016.trig.gz
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/auto-generated/datasets/geofabric.trig.gz
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/auto-generated/datasets/gnaf_current.trig.gz

#Registries
wget http://linked.data.gov.au/dataset/asgs2016/reg/?_view=reg&_format=text/turtle -O asgs2016.reg.ttl
wget http://linked.data.gov.au/dataset/geofabric/?_view=reg&_format=text/turtle -O geofabric.reg.ttl
wget http://linked.data.gov.au/dataset/gnaf/?_view=reg&_format=text/turtle -O gnafCurrent.reg.ttl

#Published Ontologies
# wget http://linked.data.gov.au/def/asgs.ttl -O asgs.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/asgs.ttl -O asgs.ont.ttl
# wget http://gnafld.net/def/gnaf.ttl -O gnaf.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/gnaf.ttl -O gnaf.ont.ttl
# wget http://www.linked.data.gov.au/def/geofabric/geofabric.ttl -O geofabric.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/geofabric.ttl -O geofabric.ont.ttl
wget https://www.opengis.net/def/appschema/hy_features/hyf/hyf.ttl -O hy_features.ont.ttl

# wget http://www.linked.data.gov.au/def/loci/loci.ttl -O loci.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/loci.ttl -O loci.ont.ttl
# wget https://raw.githubusercontent.com/CSIRO-enviro-informatics/geosparql-ext-ont/master/geox.ttl -O geox.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/geosparql-ext.ttl -O geox.ont.ttl

wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/SCHEMA_QUDT-v2.1.ttl -O SCHEMA_QUDT-v2.1.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/org.ttl -O org.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/void.ttl -O void.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/prov-o.ttl -O prov-o.ont.ttl
wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/geosparql.rdf -O geo.ont.rdf

