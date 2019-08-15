#!/bin/sh
set -e

DATASET_NAME="asgs2016"
GRAPH_NAME="http://linked.data.gov.au/dataset/asgs2016"
OUTPUT_FILE="${DATASET_NAME}.trig.gz"
ONLY_TYPE="http://linked.data.gov.au/dataset/asgs2016/stateorterritory/"

S3_BUCKET="loci-assets"
S3_REGION="ap-southeast-2"
S3_PATH="auto-generated/datasets"

if [ -z "$AWS_ACCESS_KEY_ID" ]; then echo "AWS_ACCESS_KEY_ID User needs to be set."; exit 1; fi
if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then echo "AWS_SECRET_ACCESS_KEY User needs to be set."; exit 1; fi

git clone https://github.com/CSIRO-enviro-informatics/asgs-dataset.git
cd asgs-dataset
pip install --no-cache-dir -r requirements.txt

export PYTHONPATH=$(pwd)
cd asgs_dataset
python ./app.py --init
cd ..
python ./new_graph_builder.py ${ONLY_TYPE}

cd instance

echo "<${GRAPH_NAME}> {" > head.part
echo "}" > tail.part

cat head.part *.nt tail.part | gzip -k --rsyncable > ${OUTPUT_FILE}

aws s3 cp ${OUTPUT_FILE} s3://${S3_BUCKET}/${S3_PATH}/${OUTPUT_FILE}
