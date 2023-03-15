#!/usr/bin/python3
from config import SysConfig


# STUBBED ENTRYPOINT
print(SysConfig.docker_logins)
print(SysConfig.default_container_ttl)
print(SysConfig.default_exec_timeout)
print(SysConfig.default_tag)
print(SysConfig.container_data_of_tag("default"))
print(SysConfig.container_data_of_tag("node"))
print(SysConfig.container_data_of_tag("java"))
