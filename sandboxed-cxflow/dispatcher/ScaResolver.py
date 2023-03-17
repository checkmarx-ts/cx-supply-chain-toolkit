#!/usr/bin/python3 -O
from config import SysConfig, init_logging
import sca_argparse, sys

init_logging("dispatcher")

p = sca_argparse.ScaArgsHandler(sys.argv)


# STUBBED ENTRYPOINT
print(SysConfig.default_container_ttl)
print(SysConfig.default_exec_timeout)
print(SysConfig.default_tag)
print(SysConfig.get_image_tags())
