#!/bin/sh
set -e

if [ -z "$AWS_ACCESS_KEY_ID" ]; then echo "AWS_ACCESS_KEY_ID User needs to be set."; exit 1; fi
if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then echo "AWS_SECRET_ACCESS_KEY User needs to be set."; exit 1; fi
if [ -z "$OUTPUT_FILE" ]; then echo "OUTPUT_FILE needs to be set."; exit 1; fi
if [ -z "$GRAPH_NAME" ]; then echo "GRAPH_NAME needs to be set."; exit 1; fi
if [ -z "$S3_BUCKET" ]; then echo "S3_BUCKET needs to be set."; exit 1; fi
if [ -z "$S3_REGION" ]; then echo "S3_REGION needs to be set."; exit 1; fi
if [ -z "$S3_PATH" ]; then echo "S3_PATH needs to be set."; exit 1; fi

git clone https://github.com/CSIRO-enviro-informatics/asgs-dataset.git
cd asgs-dataset
pip install --no-cache-dir -r requirements.txt

export PYTHONPATH=$(pwd)
cd asgs_dataset
python ./app.py --init
cd ..
python ./new_graph_builder.py

cd instance

echo "<${GRAPH_NAME}> {" > head.part
echo "}" > tail.part

cat head.part *.nt tail.part | gzip -k --rsyncable > ${OUTPUT_FILE}

aws s3 cp ${OUTPUT_FILE} s3://${S3_BUCKET}/${S3_PATH}/${OUTPUT_FILE}
