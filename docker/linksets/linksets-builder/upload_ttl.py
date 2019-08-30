import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os
import utils
import logging
logging.basicConfig(level=logging.DEBUG)

logging.info("Uploading linkset to s3")

utils.fail_or_getenv('AWS_ACCESS_KEY_ID')
utils.fail_or_getenv('AWS_SECRET_ACCESS_KEY')
s3_bucket = utils.fail_or_getenv('S3_BUCKET')
s3_linkset_path = utils.fail_or_getenv('S3_LINKSET_PATH')
s3_region_name = utils.fail_or_getenv('S3_REGION')
s3_client = boto3.client('s3', region_name=s3_region_name)
filename = s3_linkset_path+ '/' + "ls_mb16cc.ttl"
s3_client.upload_file('./ls_mb16cc.ttl', s3_bucket, filename[1:])
