import configparser
import sys
from default_config import default_config
from exceptions import *

def write_default_config(conf_file=None):
    print("writing default config")
    config = configparser.ConfigParser()
    config["settings"] = default_config
    if not conf_file:
        config.write()
    else:
        with open(conf_file, 'w') as configfile:
            config.write(configfile)

def read_conf(conf_file):
    config = configparser.ConfigParser()
    config.read(conf_file)
    try:
        settings = {
            "network": config["settings"]["network"], #Testnet, main, etc
            "production": config["settings"]["production"], #
            "db_dialect": config["settings"]["db_dialect"], #Name of DB service ex: postgresql
            "db_driver": config["settings"]["db_driver"], #Name of DB API ex: pg8000
            "db_username": config["settings"]["db_username"], #Username for DB login
            "db_password": config["settings"]["db_password"], #Password for DB login
            "subscribed": config["settings"]["subscribed"], #List of subscribed addresses
            "connection": "",
            }
    except:
        print("config is outdated, saving current default config to",conf_file+".sample")
        write_default_config(conf_file+".sample")
        raise

    if settings["network"].startswith("t"):
        settings["testnet"] = True

    '''Make the corresponding connection string for the DB chosen'''

    if settings["db_dialect"].lower() != 'sqlite' and settings["db_username"] == 'none':
        raise UsernameIsNull(settings["db_dialect"] + ' requires a username in config')

    if settings["db_dialect"].lower() != 'sqlite' and settings["db_password"] == 'none':
        raise PasswordIsNull(settings["db_dialect"] + ' requires a password in config')
    
    if settings["db_driver"].lower() != "none":
        db_type = settings["db_dialect"] + "+" + settings["db_driver"]
    else:
        db_type = settings["db_dialect"]

    db_login = settings["db_username"] + ":" + settings["db_password"]

    db_location = "@localhost/papi.db"

    if settings["db_dialect"].lower() == "sqlite":
        settings["connection"] = "sqlite:///data/papi.db"
    else:
        settings["connection"] = db_type + "://" + db_login + db_location

    return settings