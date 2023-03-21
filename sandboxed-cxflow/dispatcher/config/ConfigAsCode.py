import json, os
from pathlib import PurePath


def resolve_tag(input_path, default_tag, cac_filename):
    path = PurePath(input_path, cac_filename)

    if not os.path.exists(path):
        return default_tag
    else:
        with open(path, "rt") as f:
            cac = json.load(f)
            if "version" in cac.keys() and cac["version"] == "1":
                return cac["tag"]
    
    return default_tag





