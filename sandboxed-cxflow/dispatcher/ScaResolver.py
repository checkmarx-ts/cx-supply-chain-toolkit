#!/usr/bin/python3
from config import SysConfig, init_logging

init_logging("dispatcher")


# STUBBED ENTRYPOINT
print(SysConfig.default_container_ttl)
print(SysConfig.default_exec_timeout)
print(SysConfig.default_tag)
print(SysConfig.get_image_tags())
