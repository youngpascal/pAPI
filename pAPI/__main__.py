import pypeerassets as pa
import logging
import os, argparse
from appdirs import user_config_dir
from config import *


conf_dir = user_config_dir("pAPI")
conf_file = os.path.join(conf_dir, "papi.conf")

settings = {}
class Settings:
    pass

def load_conf():
    '''Load user configuration settings'''
    settings = read_conf(conf_file)

def getConnectionString():
    return settings["connection"]

def first_run():
    if not os.path.exists(conf_dir):
        os.mkdir(conf_dir)
    if not os.path.exists(conf_file):
        write_default_config(conf_file)


def main():
    first_run()

    try:
        load_conf()
    except:
        raise



if __name__ == "__main__":
    main()