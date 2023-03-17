#!/usr/bin/python3 -O
from config import SysConfig, init_logging
import sca_argparse, sys, logging

init_logging("dispatcher")

__log = logging.getLogger("ScaResolver")

sca_args = sca_argparse.ScaArgsHandler(sys.argv)

__log.debug(f"Dispatcher ScaResolver invoked with: {sca_args.get_sanitized_param_string(sca_args.get_orig_params())}")


# STUBBED ENTRYPOINT
print(SysConfig.default_container_ttl)
print(SysConfig.default_exec_timeout)
print(SysConfig.default_tag)
print(SysConfig.get_image_tags())
