import os
def fail_or_getenv(env_var_name):
    env_value = os.getenv(env_var_name)
    if env_value is None:
        raise Exception("Environment variable {env_var_name} must be defined".format(env_var_name=env_var_name))
    else:
        return env_value