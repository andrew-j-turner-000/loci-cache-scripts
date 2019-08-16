# Setting a heap of environment variables that will be common across these docker containers
# These can be `source`ed into scripts
export S3_BUCKET="loci-assets"
export S3_REGION="ap-southeast-2"
export S3_PATH="auto-generated/datasets"
export AWS_ACCESS_KEY_ID="${LOCI_S3_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${LOCI_S3_SECRET_ACCESS_KEY}"

export ASGS2016_DATASET_FILE="asgs2016.trig.gz"
export ASGS2011_DATASET_FILE="asgs2011.trig.gz"