#!/usr/bin/python3 -O
import logging, traceback
from applogging import init_logging
init_logging("dispatcher")

from pathlib import Path

from config import SysConfig, resolve_tag, Consts
__log = logging.getLogger("ScaResolver")
__log.debug("ScaResolver dispatcher is executing")


import sca_argparse, sys, os
from docker_commands import exec_docker_run
from pathlib import PurePath
from copy import deepcopy


sca_args = sca_argparse.ScaArgsHandler(sys.argv)

__log.debug(f"Dispatcher ScaResolver invoked op [{sca_args.operation}] with: {sca_args.get_sanitized_param_string(sca_args._clone_op_params())}")

def merge_with_environment(provided_env, propagate_env_keys):
    for pk in list(propagate_env_keys):
        if pk in os.environ.keys():
            provided_env[pk] = os.environ[pk]


def __convert_kv_dict_to_list(d):
    return [f"{k}={d[k]}" for k in d.keys()]

def __strip_file_part(path):
    p = Path(path)
    if len(p.suffix) == 0:
        return path
    else:
        return str(p.parent)

def __make_tuple_map(inpath, outpath, reportpath):
    m = []
    if not inpath is None:
        m.append((__strip_file_part(inpath), Consts.INPATH))

    if not outpath is None:
        m.append((__strip_file_part(outpath), Consts.OUTPATH))

    if not reportpath is None:
        m.append((__strip_file_part(reportpath), Consts.REPORTPATH))

    return m


def exec_single_stage(tag, args_array, volume_map_tuples=[]):
    containerdef = SysConfig.get_tag_definition(tag)
    dockerparams = deepcopy(containerdef.dockerparams)

    env_dict = merge_with_environment(containerdef.execenv, containerdef.envpropagate)

    if "environment" in dockerparams.keys():
        if type(dockerparams["environment"]) is dict:
            dockerparams["environment"].update(env_dict)
        elif type(dockerparams["environment"]) is list:
            dockerparams["environment"].append(__convert_kv_dict_to_list(env_dict))
    else:
        dockerparams["environment"] = env_dict

    volume_maps = (f"{PurePath(t[0])}:{PurePath(t[1])}" for t in volume_map_tuples)

    if "volumes" in dockerparams.keys():
        if type(dockerparams["volumes"]) is list:
            dockerparams["volumes"] = dockerparams["volumes"] + list(volume_maps)
        elif type(dockerparams["volumes"]) is dict:
            dockerparams["volumes"] = [f"{k}:{dockerparams['volumes'][k]['bind']}" for k in dockerparams["volumes"].keys()] + list(volume_maps)
    else:
        dockerparams["volumes"] = list(volume_maps)
   
    return exec_docker_run(containerdef.container, dockerparams, containerdef.exectimeout, SysConfig.default_delete, args_array + containerdef.execparams)

def exec_two_stage(tag):
    offline = sca_argparse.OfflineOperation(sys.argv)
    offline_args = offline.get_io_remapped_args(Consts.INPATH, Consts.OUTPATH)
    offline_map_tuples = __make_tuple_map(offline.input_path, offline.output_path, None)
    
    __log.debug(f"Executing Offline operation with args: {offline.get_sanitized_param_string(offline_args)}")
    
    result = exec_single_stage(tag, offline_args, offline_map_tuples)
    if not result == 0:
        __log.error(f"Offline operation error. Code: {result}")
        return result
    else:
        __log.debug(f"Offline operation successful")

    upload = sca_argparse.UploadOperation(sys.argv)
    upload_args = upload.get_io_remapped_args(Consts.INPATH, Consts.OUTPATH, Consts.REPORTPATH, offline.out_filename)
    upload_map_tuples = __make_tuple_map(offline.output_path, upload.output_path, upload.report_path)
    __log.debug(f"Executing Upload operation with args: {upload.get_sanitized_param_string(upload_args)}")
    result = exec_single_stage(tag, upload_args, upload_map_tuples)
    if not result == 0:
        __log.error(f"Upload operation error. Code: {result}")
    else:
        __log.debug(f"Upload operation successful")

    return result

probe = sca_argparse.ScaArgsHandler(sys.argv)
target_tag = resolve_tag(probe.input_path, SysConfig.default_tag, Consts.CAC_FILE)

__log.info(f"Executing with tag [{target_tag}]")

try:
        
    if probe.can_two_stage and SysConfig.enable_twostage:
        __log.debug("Executing as two stage.")
        sys.exit(exec_two_stage(target_tag))
    else:
        __log.debug("Executing as single stage.")
        op = sca_argparse.PassthroughOperation(sys.argv)
        maps = __make_tuple_map(op.input_path, op.output_path, op.report_path)

        sys.exit(exec_single_stage(target_tag, op.get_io_remapped_args(Consts.INPATH, Consts.OUTPATH, Consts.REPORTPATH), maps))

except Exception as ex:
    __log.error(ex)
    __log.error(traceback.format_exc())
    sys.exit(4)
