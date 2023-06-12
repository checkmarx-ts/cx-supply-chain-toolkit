import logging.config, os


def get_log_level():
    return "INFO" if os.getenv('DEBUG') is None else "DEBUG"

default_log_config = {
    "version" : 1,
    "handlers" : {
        "rotating_file" : {
            "class" : "logging.handlers.TimedRotatingFileHandler",
            "formatter" : "default",
            "level" : get_log_level(),
            "filename": "",
            "utc" : True,
            "when" : "midnight",
            "backupCount" : 7
        },
        "console" : {
            "class" : "logging.StreamHandler",
            "formatter" : "default",
            "level" : get_log_level(),
            "stream" : "ext://sys.stdout"
        }
    },
    "formatters" : {
        "default" : {
            "format" : "[%(asctime)s][%(process)d][%(name)s][%(levelname)s] %(message)s",
            "datefmt" : "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "loggers" : {
        "root" : {
            "handlers" : ["console", "rotating_file"],
            "level" : get_log_level()
        }
    }
}

def init_logging(logname):
    default_log_config["handlers"]["rotating_file"]["filename"] = f"/var/log/dispatcher/{logname}.log"
    logging.config.dictConfig(default_log_config)
