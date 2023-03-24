import logging, docker
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
    if docker_params is None:
        docker_params = {"detach" : True}
    else:
        docker_params["detach"] = True

    ret_code = {"StatusCode" : 8192}

    inst = __client.containers.run(tag, command=app_params, **docker_params)
    __log.info(f"Container [{inst.name}] started with id [{inst.short_id}]")
    try:
        ret_code = inst.wait(timeout=timeout.total_seconds())
    except inst.exceptions.ReadTimeout:
        inst.kill()
    finally:
        if not inst is None:
            for line in inst.logs(stream=True):
                __log.debug(line.decode('utf-8'))

            inst.remove(v=True, force=True)
    return ret_code['StatusCode']


