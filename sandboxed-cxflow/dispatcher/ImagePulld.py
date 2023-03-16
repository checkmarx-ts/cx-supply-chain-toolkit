#!/usr/bin/python3 -O
import logging
from config import SysConfig, init_logging
init_logging("imagepulld")
__log = logging.getLogger("daemon")

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
    proc = psutil.Process(os.getpid())

    keep_fds = [f.fd for f in proc.open_files()]

    with daemon.DaemonContext(files_preserve=keep_fds):
        daemon_loop()
else:
    daemon_loop()
