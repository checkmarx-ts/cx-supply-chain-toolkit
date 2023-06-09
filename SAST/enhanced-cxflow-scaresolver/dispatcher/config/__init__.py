from pathlib import Path
import yaml, sys, re, os
from .ConfigProvider import ConfigProvider
from .ConfigAsCode import resolve_tag


def locate_config_yaml():
    loc = Path(os.path.dirname(sys.argv[0]))

    yaml_file = None

    if os.path.exists(loc / "yaml"):
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
    return load_yaml(locate_config_yaml())


SysConfig = ConfigProvider(load_default_yaml())

class Consts:
    INPATH = "/sandbox/input_sandbox"
    OUTPATH = "/sandbox/output"
    REPORTPATH = "/sandbox/report"
    CAC_FILE = ".cxsca"

