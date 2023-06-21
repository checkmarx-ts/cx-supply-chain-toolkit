import logging

import os, re
from datetime import timedelta
from .ImageTagDefinition import ImageTagDefinition


class ConfigProvider:
    __log = logging.getLogger("ConfigProvider")
    
    def __init__(self, the_yaml):
        self.__yaml = the_yaml
        tag_defs = ConfigProvider._navigate_or_else(self.__yaml, lambda: {}, ["resolver", "images"])

        # It is possible there are no tags defined in a file, so resolve others defined in
        # environment variables.
        env_tag_defs = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_.*")

        for env_tag_def in env_tag_defs:
            components = re.match("^RESOLVER_IMAGES_(?P<tag>.+?)_.+$", env_tag_def).groupdict()
            if not components["tag"].lower() in tag_defs.keys():
                tag_defs[components["tag"].lower()] = {}

        self.__tags = { tag:self.__load_tag_config(tag) for tag in tag_defs.keys()} if not tag_defs == None else {}



    @staticmethod
    def __find_matching_environment_keys(matchspec):
        return [k for k in os.environ.keys() if not re.search(matchspec, k) is None]
    
    @staticmethod
    def __timedelta_from_string(spec):

        def parse_value(type):
            pattern = f".*?(?P<value>\d+?){type}"
            value = re.match(pattern, spec)
            return int(value.groupdict()["value"]) if not value is None and "value" in value.groupdict().keys() else 0
    
        seconds = parse_value("s")
        minutes = parse_value("m")
        hours = parse_value("h")

        return timedelta(seconds=seconds, minutes=minutes, hours=hours)


    @staticmethod
    def __translate_environment_hostname(encoded_hostname):
        dash_placeholders = encoded_hostname.split("__")

        hostname = "" if len(dash_placeholders) > 0 else encoded_hostname

        for component in dash_placeholders:
            if len(hostname) > 0:
                hostname = hostname + "-" + component
            else:
                hostname = component

        dot_placeholders = hostname.split("_")

        hostname = "" if len(dot_placeholders) > 0 else hostname 
        for component in dot_placeholders:
            if len(hostname) > 0:
                hostname = hostname + "." + component
            else:
                hostname = component
       
        return hostname


    @staticmethod
    def _navigate_or_else(yaml_dict, func, list):
        if list is None or yaml_dict is None:
            return func()
        elif len(list) == 0:
            return yaml_dict
        elif list[0] in yaml_dict.keys() and type(yaml_dict[list[0]]) is dict:
            return ConfigProvider._navigate_or_else(yaml_dict[list[0]], func, list[1:])
        elif not list[0] in yaml_dict.keys():
            return func()
        else:
            return yaml_dict[list[0]]
            
        




    @staticmethod
    def __environment_override (orig_value, environment_var, convert_func=None):
        if environment_var in os.environ.keys():
            return convert_func(os.environ[environment_var]) if not convert_func is None else os.environ[environment_var]
        else:
            return orig_value

    @property
    def __docker_logins(self):
        if not hasattr(self, "_docker_logins"):
            
            ret = ConfigProvider._navigate_or_else(self.__yaml, lambda: {}, ["docker","login"])

            env = ConfigProvider.__find_matching_environment_keys("^DOCKER_LOGIN_.*")
            for e in env:
                components = re.match("^DOCKER_LOGIN_(?P<host>.+?)_(?P<variable>USERNAME|PASSWORD)$", e).groupdict()
                value = os.environ[e]
                host = ConfigProvider.__translate_environment_hostname(components["host"]).lower()
                if not host in ret.keys():
                    ret[host] = {}
                
                ret[host][components["variable"].lower()] = value

            self._docker_logins = ret

        return self._docker_logins
    
    @property
    def docker_registry_servers(self):
        return self.__docker_logins.keys()
    
    def get_docker_registry_username(self, server):
        return self.__docker_logins[server]["username"]

    def get_docker_registry_password(self, server):
        return self.__docker_logins[server]["password"]

    
    @property
    def default_container_ttl(self):
        if not hasattr(self, "_container_ttl"):
            self._container_ttl =  ConfigProvider.__timedelta_from_string \
                (str(ConfigProvider._navigate_or_else(self.__yaml, lambda: "1h", ["resolver","defaults","containerttl"])))
            
            self._container_ttl =  ConfigProvider.__environment_override(self._container_ttl, \
                                        "RESOLVER_DEFAULTS_CONTAINERTTL", lambda x: ConfigProvider.__timedelta_from_string(x) )
       
        return self._container_ttl


    @property
    def default_exec_timeout(self):
        if not hasattr(self, "_exec_timeout"):
            self._exec_timeout =  ConfigProvider.__timedelta_from_string \
                (str(ConfigProvider._navigate_or_else(self.__yaml, lambda: "30m", ["resolver","defaults","exectimeout"])))

            self._exec_timeout =  ConfigProvider.__environment_override(self._exec_timeout, "RESOLVER_DEFAULTS_EXECTIMEOUT", 
                                                                        lambda x: ConfigProvider.__timedelta_from_string(x))
       
        return self._exec_timeout

    @property
    def default_tag(self):
        if not hasattr(self, "_default_tag"):
            self._default_tag =  str(ConfigProvider._navigate_or_else(self.__yaml, lambda: "default", ["resolver","defaults","defaulttag"]))
            self._default_tag =  ConfigProvider.__environment_override(self._default_tag, "RESOLVER_DEFAULTS_DEFAULTTAG")
       
        return self._default_tag

    @property
    def default_delete(self):
        if not hasattr(self, "_default_delete"):
            self._default_delete =  bool(ConfigProvider._navigate_or_else(self.__yaml, lambda: True, ["resolver","defaults","delete"]))
            self._default_delete =  bool(ConfigProvider.__environment_override(self._default_delete, "RESOLVER_DEFAULTS_DELETE"))
       
        return self._default_delete

    @staticmethod
    def __str_to_bool(s):
        if s.isnumeric():
            return bool(int(s))
        else:
            return True if s.lower() == 'true' else False


    @property
    def enable_twostage(self):
        if not hasattr(self, "_twostage"):
            self._twostage =  bool(ConfigProvider._navigate_or_else(self.__yaml, lambda: True, ["resolver","twostage"]))
            self._twostage =  ConfigProvider.__environment_override(self._twostage, "RESOLVER_TWOSTAGE", ConfigProvider.__str_to_bool)
       
        return self._twostage
    

    def __load_tag_config(self, tag):
        image_configs = ConfigProvider._navigate_or_else(self.__yaml, lambda: None, ["resolver", "images"])
        image_config = image_configs[tag] if not image_configs is None else {}

        if image_config == None and self.default_tag in image_configs.keys():
            return self.__load_tag_config(self.default_tag)
        elif image_config == None:
            raise Exception(f"No image definition available for tag {tag}!")
        
        container_matches = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_{tag.upper()}_CONTAINER$")
        if len(container_matches) > 0:
            image_config["container"] = os.environ[container_matches[0]]

        containerttl_matches = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_{tag.upper()}_CONTAINERTTL$")
        if len(containerttl_matches) > 0:
            image_config["containerttl"] = os.environ[containerttl_matches[0]]

        exectimeout_matches = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_{tag.upper()}_EXECTIMEOUT$")
        if len(exectimeout_matches) > 0:
            image_config["exectimeout"] = os.environ[exectimeout_matches[0]]

        execenv_matches = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_{tag.upper()}_EXECENV_.+$")
        if len(execenv_matches) > 0:
            for v in execenv_matches:
                varname_match = re.match(f"^RESOLVER_IMAGES_{tag.upper()}_EXECENV_(?P<variable>.+)$", v)
                if image_config["execenv"] == None:
                    image_config["execenv"] = {}
                image_config["execenv"][varname_match.groupdict()["variable"]] = os.environ[v]

        execparam_matches = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_{tag.upper()}_EXECPARAMS_\d+$")
        if len(execparam_matches) > 0:
            image_config["execparams"] = [os.environ[v] for v in execparam_matches]

        envpropagate_matches = ConfigProvider.__find_matching_environment_keys(f"^RESOLVER_IMAGES_{tag.upper()}_ENVPROPAGATE_\d+$")
        if len(envpropagate_matches) > 0:
            image_config["envpropagate"] = [os.environ[v] for v in envpropagate_matches]

        ttl = ConfigProvider._navigate_or_else(image_config, lambda: None, ["containerttl"])
        if ttl == None:
            ttl = self.default_container_ttl
        else:
            ttl = ConfigProvider.__timedelta_from_string(ttl)

        timeout = ConfigProvider._navigate_or_else(image_config, lambda: None,["exectimeout"])
        if timeout == None:
            timeout = self.default_exec_timeout
        else:
            timeout = ConfigProvider.__timedelta_from_string(timeout)

        return ImageTagDefinition(image_config["container"],
                                  ttl,
                                  timeout,
                                  ConfigProvider._navigate_or_else(image_config, lambda: {}, ["execenv"]),
                                  ConfigProvider._navigate_or_else(image_config, lambda: [],["execparams"]),
                                  ConfigProvider._navigate_or_else(image_config, lambda: [], ["envpropagate"]),
                                  ConfigProvider._navigate_or_else(image_config, lambda: {}, ["dockerparams"]))

   
    def get_image_tags(self):
        return [str(c.container) for c in self.__tags.values()]

    def get_tags(self):
        return self.__tags.keys()

    def get_tag_definition(self, tag):
        if not tag in self.__tags.keys():
            ConfigProvider.__log.warn(f"Tag [{tag}] not found, using default tag of [{self.default_tag}]")
            return self.get_default_tag_definition()
        
        return self.__tags[tag]
     
    def get_default_tag_definition(self):
        if not self.default_tag in self.__tags.keys():
            msg = f"Default tag [{self.default_tag}] is not defined, can't continue."
            ConfigProvider.__log.error(msg)
            raise RuntimeError(msg)
        
        return self.__tags[self.default_tag]
  
