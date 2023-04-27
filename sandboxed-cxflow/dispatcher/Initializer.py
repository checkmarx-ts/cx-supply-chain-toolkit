#!/usr/bin/python3 -O
from applogging import init_logging
init_logging("initializer")

from config import SysConfig

from docker_commands import exec_docker_login, exec_docker_pull

import logging
__log = logging.getLogger("Initializer")

def do_docker_logins():
    for server in SysConfig.docker_registry_servers:
        __log.info(f"Login to docker registry @ {server}")
        exec_docker_login(server, SysConfig.get_docker_registry_username(server), SysConfig.get_docker_registry_password(server))


def do_docker_pulls():
    for t in SysConfig.get_image_tags():
        exec_docker_pull(t)
    pass


if __name__ == "__main__":
    do_docker_logins()
    do_docker_pulls()

    

