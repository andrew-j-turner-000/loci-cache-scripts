import os
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)

def run_command(command_line_array):
    '''
    Utility for running commands and logging outputs
    '''
    output = ''
    logging.debug(command_line_array)
    output = subprocess.check_output(command_line_array, universal_newlines=True)
    logging.info(output)


def fail_or_getenv(env_var_name, warn_only=False):
    env_value = os.getenv(env_var_name)
    if env_value is None:
        if warn_only:
            logging.warn("Environment variable {env_var_name} is not defined".format(env_var_name=env_var_name))
            return None
        raise Exception("Environment variable {env_var_name} must be defined".format(env_var_name=env_var_name))
    else:
        return env_value
