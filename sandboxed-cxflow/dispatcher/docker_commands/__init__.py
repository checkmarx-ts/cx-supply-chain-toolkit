import subprocess
import logging, io

__log = logging.getLogger("docker_commands")

def __exec(command, params, stdin=None):
    stdout = None

    __log.debug(f"Executing docker command {command}")
    
    proc = None

    try:
        proc = subprocess.run(["docker", command] + params, stdin=stdin, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = proc.stdout
        __log.info(f"Docker command {command} execution success with exit code {proc.returncode}")
    except subprocess.CalledProcessError as ex:
        __log.error(f"Docker command {command} execution failed with exit code {ex.returncode}")
        stdout = ex.stdout

    if __log.isEnabledFor(logging.DEBUG):
        with io.TextIOWrapper(io.BytesIO(stdout)) as s:
            prev = -1
            while True:
                if s.tell() == prev:
                    break
                prev = s.tell()
                log = s.readline()
                __log.debug(log)
        
    return proc.returncode
    



def exec_docker_login(server, username, password, *arg, **kwargs):
    params = ["-u", username, "-p", password, server]
    return __exec("login", params)

def exec_docker_pull(tag):
    __log.info(f"Pulling docker image with tag {tag}")
    params = ["-q", tag]
    return __exec("pull", params)

def exec_docker_run(tag, environment, docker_params, app_params=[]):
    default_params = ["--rm"]
    env_opts = []
    for k in environment.keys():
        env_opts.append("--env")
        env_opts.append(f"{k}={environment[k]}")

    __log.debug(['docker', 'run'] + default_params + docker_params + environment + [tag] + app_params)


