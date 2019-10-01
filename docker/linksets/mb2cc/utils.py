import os
import subprocess
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import logging
logging.basicConfig(level=logging.DEBUG)

def run_command(command_line_array):
    '''
    Utility for running commands and logging outputs
    '''
    output = ''
    logging.debug(' '.join(command_line_array))
    output = subprocess.check_output(command_line_array, universal_newlines=True)
    logging.info(output)

def alter_column_name(table_name, column_name, new_column_name):
    '''
    Change the name of a column in a table
    '''
    create_intersection_sql = """ALTER TABLE \"{table_name}\" RENAME \"{column_name}\" TO \"{new_column_name}\";"""\
        .format(table_name=table_name, column_name=column_name, new_column_name=new_column_name)
    run_command(["psql", "--host", "postgis", "--user",
                 "postgres", "-d", "mydb", "-c", create_intersection_sql])


def fail_or_getenv(env_var_name, warn_only=False):
    env_value = os.getenv(env_var_name)
    if env_value is None:
        if warn_only:
            logging.warn("Environment variable {env_var_name} is not defined".format(env_var_name=env_var_name))
            return None
        raise Exception("Environment variable {env_var_name} must be defined".format(env_var_name=env_var_name))
    else:
        return env_value

def upload_ttl(target_s3_file, local_source_file):
    logging.info("Uploading {} to s3".format(local_source_file))
    fail_or_getenv('AWS_ACCESS_KEY_ID')
    fail_or_getenv('AWS_SECRET_ACCESS_KEY')
    linkset_file = target_s3_file 
    s3_bucket = fail_or_getenv('S3_BUCKET')
    s3_linkset_path = fail_or_getenv('S3_LINKSET_PATH')
    s3_region_name = fail_or_getenv('S3_REGION')
    s3_client = boto3.client('s3', region_name=s3_region_name)
    filename = s3_linkset_path+ '/' + linkset_file 
    s3_client.upload_file(local_source_file, s3_bucket, filename[1:])


