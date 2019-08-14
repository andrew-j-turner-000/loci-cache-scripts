#!/bin/sh

#Linksets
wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/linksets/ls_mb16cc.ttl'
wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/linksets/ls_addrcatch.trig'

#mb11mb16
#addrcatch-linkset
#addrmb11-linkset
#addrmb16-linkset
#addr1605mb11-linkset
#addr1605mb16-linkset

#Datasets
wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/auto-generated/datasets/asgs2016.trig.gz'
wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/auto-generated/datasets/geofabric.trig.gz'
wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/auto-generated/datasets/gnaf_current.trig.gz'

#Registries
wget 'http://linked.data.gov.au/dataset/asgs2016/reg/?_view=reg&_format=text/turtle' -O asgs2016.reg.ttl
wget 'http://linked.data.gov.au/dataset/geofabric/?_view=reg&_format=text/turtle' -O geofabric.reg.ttl
wget 'http://linked.data.gov.au/dataset/gnaf/?_view=reg&_format=text/turtle' -O gnafCurrent.reg.ttl

#Externally published Ontologies
wget --header='Accept: text/turtle' http://linked.data.gov.au/def/asgs -O asgs.ont.ttl
# wget --header='Accept: text/turtle' https://raw.githubusercontent.com/AGLDWG/asgs-ont/master/asgs.ttl -O asgs.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/asgs.ttl' -O asgs.ont.ttl
wget --header='Accept: text/turtle' http://linked.data.gov.au/def/gnaf -O gnaf.ont.ttl
# wget --header='Accept: text/turtle' https://raw.githubusercontent.com/AGLDWG/gnaf-ont/master/gnaf.ttl -O gnaf.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/gnaf.ttl' -O gnaf.ont.ttl
wget --header='Accept: text/turtle' http://linked.data.gov.au/def/geofabric -O geofabric.ont.ttl
# wget --header='Accept: text/turtle' https://raw.githubusercontent.com/CSIRO-enviro-informatics/geofabric-ont/master/geofabric.ttl -O gnaf.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/geofabric.ttl' -O geofabric.ont.ttl
wget 'https://www.opengis.net/def/appschema/hy_features/hyf/hyf.ttl' -O hy_features.ont.ttl
wget --header='Accept: text/turtle' http://qudt.org/2.0/schema/SCHEMA_QUDT-v2.0.ttl -O SCHEMA_QUDT-v2.1.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/SCHEMA_QUDT-v2.1.ttl' -O SCHEMA_QUDT-v2.1.ont.ttl
wget --header='Accept: text/turtle' http://www.w3.org/ns/org -O org.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/org.ttl' -O org.ont.ttl
wget --header='Accept: text/turtle' http://rdfs.org/ns/void -O void.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/void.ttl' -O void.ont.ttl
wget --header='Accept: text/turtle' http://www.w3.org/ns/prov -O prov-o.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/prov-o.ttl' -O prov-o.ont.ttl
wget --header='Accept: application/rdf+xml' http://www.opengis.net/ont/geosparql -O geo.ont.rdf
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/geosparql.rdf' -O geo.ont.rdf

#Local ontologies
# wget http://www.linked.data.gov.au/def/loci/loci.ttl -O loci.ont.ttl
wget --header='Accept: text/turtle' https://raw.githubusercontent.com/CSIRO-enviro-informatics/loci-ont/master/loci.ttl -O loci.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/loci.ttl' -O loci.ont.ttl
wget --header='Accept: text/turtle' https://raw.githubusercontent.com/CSIRO-enviro-informatics/geosparql-ext-ont/master/geox.ttl -O geox.ont.ttl
# wget 'https://loci-assets.s3-ap-southeast-2.amazonaws.com/ontologies/loci-lite/geosparql-ext.ttl' -O geox.ont.ttl


