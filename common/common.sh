# Setting a heap of environment variables that will be common across these docker containers
# These can be `source`ed into scripts

export AWS_ACCESS_KEY_ID="${LOCI_S3_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${LOCI_S3_SECRET_ACCESS_KEY}"

export S3_BUCKET="loci-assets"
export S3_REGION="ap-southeast-2"

#This is the used to create and consume the datasets 
export S3_DATASET_PATH="/auto-generated/datasets"
export ASGS2016_DATASET_FILE="asgs2016.trig.gz"
export ASGS2011_DATASET_FILE="asgs2011.trig.gz"
export GEOFABRIC_DATASET_FILE="geofabric.trig.gz"
export GNAF_DATASET_FILE="gnaf_current.trig.gz"
export GNAF1605_DATASET_FILE="gnaf_1605.trig.gz"

#This is the used to create and consume the linksets 
export S3_LINKSET_PATH="/linksets" #Eventually "/auto-generated/linksets"
export MB2CC_LINKSET_FILE="ls_mb16cc.ttl"
export ADDR2CC_LINKSET_FILE="ls_addrcatch.trig"
export MB11MB16_LINKSET_FILE="ls_mb11mb16.trig.gz"
