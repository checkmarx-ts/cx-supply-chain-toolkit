import subprocess
import logging, io, docker
from urllib3.util import Url

__log = logging.getLogger("docker_commands")

__client = docker.from_env()

    
def exec_docker_login(server, username, password):
    return __client.login(username=username, password=password, registry=str(Url(scheme="https", host=server)))

def exec_docker_pull(tag):
    __log.info(f"Pulling docker image with tag {tag}")
    image_spec = tag.split(':')
    if len(image_spec) > 0:
        try:
            img = __client.images.pull(image_spec[0], tag=image_spec[1] if len(image_spec) > 0 else None)
            return img
        except docker.errors.APIError as e:
            __log.warn(f"Unable to pull image with tag {tag}.")
            __log.debug(e)
    return None

def exec_docker_run(tag, docker_params, timeout, app_params=[]):
    env_opts = []

    # TODO: docker_params will be the kwargs sent to the API.  Change docs, reference
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run

    # TODO: Check docker_params environment as a dict or list.  Append as appropriate.
    # if not environment is None:
    #     for k in environment.keys():
    #         env_opts.append("--env")
    #         env_opts.append(f"{k}={environment[k]}")

    # TODO: check if "detach" is in docker params, set it to True or add it as True





    return 0


