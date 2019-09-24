import os
import subprocess
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
