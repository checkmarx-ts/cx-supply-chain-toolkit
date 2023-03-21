#!/usr/bin/python3 -O
from config import SysConfig, init_logging, resolve_tag
import sca_argparse, sys, logging, os
from docker_commands import exec_docker_run
from pathlib import PurePath

init_logging("dispatcher")

__log = logging.getLogger("ScaResolver")

sca_args = sca_argparse.ScaArgsHandler(sys.argv)

__log.debug(f"Dispatcher ScaResolver invoked with: {sca_args.get_sanitized_param_string(sca_args._clone_op_params())}")

def merge_with_environment(provided_env, propagate_env_keys):
    for pk in list(propagate_env_keys):
        if pk in os.environ.keys():
            provided_env[pk] = os.environ[pk]

def exec_single_stage(tag, args_array, volume_map_tuples=[]):
    containerdef = SysConfig.get_tag_definition(tag)
    env_dict = merge_with_environment(containerdef.execenv, containerdef.envpropagate)
    volume_maps = []
    for t in volume_map_tuples:
        volume_maps.append("-v")
        volume_maps.append(f"{PurePath(t[0])}:{PurePath(t[1])}")

    return exec_docker_run(containerdef.container, env_dict, 
                           containerdef.dockerparams + volume_maps, args_array + containerdef.execparams)

def exec_two_stage(tag):
    offline = sca_argparse.OfflineOperation(sys.argv)
    offline_args = offline.get_io_remapped_args("/sandbox/input", "/sandbox/output")
    offline_map_tuples = [(offline.input_path, "/sandbox/input"), (offline.output_path, "/sandbox/output")]
    
    __log.debug(f"Executing Offline operation with args: {offline.get_sanitized_param_string(offline_args)}")
    
    result = exec_single_stage(tag, offline_args, offline_map_tuples)
    if not result == 0:
        __log.error(f"Offline operation error. Code: {result}")
        return result
    else:
        __log.debug(f"Offline operation successful")

    upload = sca_argparse.UploadOperation(sys.argv)
    upload_args = upload.get_remapped_args("/sandbox/input")
    upload_map_tuples = [(offline.output_path, "/sandbox/input")]
    __log.debug(f"Executing Upload operation with args: {upload.get_sanitized_param_string(upload_args)}")
    result = exec_single_stage(tag, upload_args, upload_map_tuples)
    if not result == 0:
        __log.error(f"Upload operation error. Code: {result}")
    else:
        __log.debug(f"Upload operation successful")

    return result

probe = sca_argparse.ScaArgsHandler(sys.argv)
target_tag = resolve_tag(probe.input_path, SysConfig.default_tag, ".cxsca")

__log.info(f"Executing with tag [{target_tag}]")

if probe.can_two_stage:
    sys.exit(exec_two_stage(target_tag))
else:
    sys.exit(exec_single_stage(target_tag, sca_argparse.PassthroughOperation(sys.argv).get_io_remapped_args("/sandbox/input", "/sandbox/output")))

