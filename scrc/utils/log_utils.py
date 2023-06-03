from root import ROOT_DIR
import os
import yaml
import logging.config
import logging
import coloredlogs

from dotenv import load_dotenv

load_dotenv()


def get_logger(name='debug_logger', default_path=ROOT_DIR / 'logging.yaml', default_level=logging.INFO,
               env_key='LOG_CFG'):
    """
    | **@author:** Prathyush SP
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                print('config load success')
                try: #Try to isolate error
                    logging.config.dictConfig(config)
                except Exception as e: #Try to isolate error
                    print("Failed to configure logging: ", str(e))
                #logging.config.dictConfig(config)
                #print('logging_loading success')
                coloredlogs.install()
                print('coloredlogs install succes')
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')

    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOGLEVEL", "DEBUG"))
    return logger

