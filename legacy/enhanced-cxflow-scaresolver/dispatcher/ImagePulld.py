#!/usr/bin/python3 -O
from applogging import init_logging
init_logging("imagepulld")

import logging
__log = logging.getLogger("daemon")

from config import SysConfig
import daemon, time, sched, psutil, os
from docker_commands import exec_docker_pull

schedule = sched.scheduler(time.time, time.sleep)

def exec_and_reschedule(container_tag, delay, priority):
    exec_docker_pull(container_tag)
    schedule.enter(delay, priority, exec_and_reschedule, [container_tag, delay, priority])


def daemon_loop():
    priority = 0
    
    for t in SysConfig.get_tags():
        tag_def = SysConfig.get_tag_definition(t)
        __log.info(f"Tag [{t}] for container [{tag_def.container}] update cycle: {tag_def.containerttl.total_seconds()} seconds")
        schedule.enter(tag_def.containerttl.total_seconds(), priority, exec_and_reschedule, [tag_def.container, 
            tag_def.containerttl.total_seconds(), priority] )
        priority = priority + 1

    schedule.run()

if not __debug__:
    __log.debug("Creating Process object")
    proc = psutil.Process(os.getpid())
    __log.debug("Process object created")

    
    __log.debug(f"Getting open file descriptors for [{str(proc)}]")
    keep_fds = [f.fd for f in proc.open_files()]
    __log.debug(f"{len(keep_fds)} file descriptors found.")

    __log.debug("Starting daemon loop")
    with daemon.DaemonContext(files_preserve=keep_fds, detach_process=True):
        daemon_loop()
else:
    daemon_loop()
