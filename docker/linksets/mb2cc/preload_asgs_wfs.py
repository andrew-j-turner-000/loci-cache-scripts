import zipfile
import os
import utils
import logging
import boto3
logging.basicConfig(level=logging.DEBUG)

utils.fail_or_getenv('AWS_ACCESS_KEY_ID')
utils.fail_or_getenv('AWS_SECRET_ACCESS_KEY')
s3_bucket = utils.fail_or_getenv('S3_BUCKET')
s3_source_data_path = utils.fail_or_getenv('S3_SOURCE_DATA_PATH')
s3_asgs_2016_mb_path = utils.fail_or_getenv('S3_ASGS_2016_MB_PATH')
asgs_mb_wfs_url = utils.fail_or_getenv('ASGS_MB_WFS_URL')
s3_region_name = utils.fail_or_getenv('S3_REGION')
local_name_prefix = utils.fail_or_getenv("ASGS_MB_LOCAL_NAME_PREFIX")


def dump_local_asgs_mb():
    '''
    Dump WFS meshblocks to a local shapefile 
    '''
    logging.info("Dumping meshblocks from WFS service")
    source_data = "WFS:{}".format(asgs_mb_wfs_url)
    utils.run_command(["ogr2ogr", local_name_prefix, source_data])
    with zipfile.ZipFile('{}.zip'.format(local_name_prefix), 'w') as myzip:
        for folderName, subfolders, filenames in os.walk('./{}'.format(local_name_prefix)):
            for filename in filenames:
                myzip.write(os.path.join(folderName, filename))


def upload_asgs_mb_s3():
    '''
    Upload the asgs file created to s3 for later use 
    '''
    logging.info("Uploading meshblocks file to S3")
    s3_client = boto3.client('s3', region_name=s3_region_name)
    s3_client.upload_file('./'+local_name_prefix+'.zip', s3_bucket, (s3_source_data_path + s3_asgs_2016_mb_path)[1:])


if __name__ == '__main__':
    dump_local_asgs_mb()
    upload_asgs_mb_s3()
