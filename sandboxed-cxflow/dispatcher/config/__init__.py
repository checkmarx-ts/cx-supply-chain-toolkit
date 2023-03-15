from pathlib import Path
import yaml, sys, re, os, logging.config
from .ConfigProvider import ConfigProvider


def get_log_level():
    return "INFO" if os.getenv('DEBUG') is None else "DEBUG"

default_log_config = {
    "version" : 1,
    "handlers" : {
        "console" : {
            "class" : "logging.StreamHandler",
            "formatter" : "default",
            "level" : get_log_level(),
            "stream": "ext://sys.stdout"
        }
    },
    "formatters" : {
        "default" : {
            "format" : "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt" : "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "loggers" : {
        "root" : {
            "handlers" : ["console"],
            "level" : get_log_level()
        }
    }
}

logging.config.dictConfig(default_log_config)

def locate_yaml():
    loc = Path(os.path.dirname(sys.argv[0]))

    yaml_file = None

    for x in (loc / "yaml").iterdir():
        if re.search(".*\.y.?ml$", str(x)):
            yaml_file = x

    return yaml_file


def load_yaml(path):
    if not path is None:
        with open(path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    else:
        return {}

def load_default_yaml():
    return load_yaml(locate_yaml())


SysConfig = ConfigProvider(load_default_yaml())



