import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os
import utils
import logging
logging.basicConfig(level=logging.DEBUG)

logging.info("Uploading linkset to s3")
target_s3_file = utils.fail_or_getenv('MB2CC_LINKSET_FILE')
local_file_path = './ls_mb16cc.ttl'
utils.upload_ttl(target_s3_file, local_file_path)