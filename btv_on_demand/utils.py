import os

import pytimeparse

def get_resource_path(path=''):
    '''
    Get the path to the source files and resources.
    '''

    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)

def get_storage_path(path=''):
    '''
    Get the path to a folder where application resources can be stored.
    '''

    if (is_env_override('BTV_STORAGE_PATH')):
        return get_env_override('BTV_STORAGE_PATH')

    base_path = os.path.expanduser('~')
    folder_path = os.path.join(base_path, '.btv-on-demand')

    if (not os.path.exists(folder_path)):
        os.mkdir(folder_path)

    return os.path.join(folder_path, path)

def get_env_override(var_name, default=None):
    '''
    Return the given variable from the environment if it exists.

    Otherwise return `default`.
    '''

    if (is_env_override(var_name)):
        return os.environ[var_name]
    else:
        return default

def is_env_override(var_name):
    '''
    Check if a settings is overriden by the environment.
    '''
    return (var_name in os.environ and len(os.environ[var_name]) > 0)

def parse_time_to_s(time_str):
    '''
    Parse a loosely formatted time string into integer seconds.
    '''

    if (time_str is None):
        return None

    try:
        return pytimeparse.parse(time_str)
    except Exception as e:
        print(f'Could not parse time: {time_str}')
        return None

def safe_walk(data_dict, key_list):
    '''
    Return the value at the end of `walk_list` or `None`
    if any path along the way does not exist.
    '''

    current = data_dict
    for key in key_list:
        if (not hasattr(current, '__contains__')):
            return None

        if (key in current):
            current = current[key]
        else:
            return None

    return current


