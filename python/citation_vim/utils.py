# -*- coding: utf-8 -*-

import sys
import re
import os.path
from datetime import datetime, timedelta
import pickle

def compat_str(string):
    if sys.version_info[0] == 2:
        return unicode(string)
    elif sys.version_info[0] == 3:
        return str(string)

def decode_str(string):
    if sys.version_info[0] == 2:
        return string.decode(encoding='UTF-8')
    elif sys.version_info[0] == 3:
        return string

def is_current(file_path, cache_path):
    if not os.path.isfile(file_path):
        raiseError(u"{} does not exist".format(file_path))
    if not os.path.isfile(cache_path):
        return False

    filetime = datetime.fromtimestamp(os.path.getctime(file_path))
    cachetime = datetime.fromtimestamp(os.path.getctime(cache_path))
    return filetime < cachetime

def check_path(path):
    path = os.path.abspath(os.path.expanduser(path))
    return os.path.exists(path)

def raiseError(message):
    raise RuntimeError(u"Citation.vim error: " + message)

def strip_braces(string):
    return re.sub("[{.*}]+", "", string) 

def read_cache(cache_file):
    """
    Returns items from the cache file.
    """
    with open(cache_file, 'rb') as in_file:
        return pickle.load(in_file)

def write_cache(cache_file, items):
    """
    Writes the cache file.
    """
    with open(cache_file, 'wb') as out_file:
        pickle.dump(items, out_file)
