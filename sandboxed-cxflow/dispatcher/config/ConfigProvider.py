import os, re
from datetime import timedelta
from dateutil.parser import parse
from .ImageTagDefinition import ImageTagDefinition

class ConfigProvider:
    def __init__(self, the_yaml):
        self.__yaml = the_yaml
        self.__tags = {}


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
    def _navigate_or_else(yaml_dict, func):
        
        class Wrapper:
            def __init__(self, obj, end=False):
                self.__the_wrapped_object = obj
                self.__the_func = func
                self.__the_end = end

            def __str__(self):
                return str(self.__the_wrapped_object)
            
            def __len__(self):
                return len(self.__the_wrapped_object)
            
            def __eq__(self, other):
                return self.__the_wrapped_object == other
            
            def __getattr__(self, name):
                if not hasattr(self.__the_wrapped_object, name):
                    raise AttributeError(name)
                else:
                    return getattr(self.__the_wrapped_object, name)

            def __setitem__(self, key, value):
                self.__the_wrapped_object[key] = value

            def __getitem__(self, items):

                if self.__the_end:
                    return self.__the_wrapped_object

                if not items in self.__the_wrapped_object.keys():
                    return Wrapper(self.__the_func(), True)
                else:
                    if type(self.__the_wrapped_object[items]) is dict:
                        return ConfigProvider._navigate_or_else(self.__the_wrapped_object[items], self.__the_func)
                    else:
                        return self.__the_wrapped_object[items] if not self.__the_wrapped_object[items] is None else self.__the_func()
                
        return Wrapper(yaml_dict)


    @staticmethod
    def __environment_override (orig_value, environment_var):
        if environment_var in os.environ.keys():
            return os.environ[environment_var]
        else:
            return orig_value

    @property
    def docker_logins(self):
        ret = ConfigProvider._navigate_or_else(self.__yaml, lambda: {} )["docker"]["login"]

        env = ConfigProvider.__find_matching_environment_keys("^DOCKER_LOGIN_.*")
        for e in env:
            components = re.match("^DOCKER_LOGIN_(?P<host>.+?)_(?P<variable>USERNAME|PASSWORD)$", e).groupdict()
            value = os.environ[e]
            host = ConfigProvider.__translate_environment_hostname(components["host"]).lower()
            if not host in ret.keys():
                ret[host] = {}
            
            ret[host][components["variable"].lower()] = value

        return ret
    

    @property
    def default_container_ttl(self):
        if not hasattr(self, "_container_ttl"):
            self._container_ttl =  ConfigProvider.__timedelta_from_string \
                (str(ConfigProvider._navigate_or_else(self.__yaml, lambda: "1h")["resolver"]["defaults"]["containerttl"]))
            self._container_ttl = ConfigProvider.__timedelta_from_string \
                (ConfigProvider.__environment_override(self._container_ttl, "RESOLVER_DEFAULTS_CONTAINERTTL"))
       
        return self._container_ttl

    @property
    def default_exec_timeout(self):
        if not hasattr(self, "_exec_timeout"):
            self._exec_timeout =  ConfigProvider.__timedelta_from_string \
                (str(ConfigProvider._navigate_or_else(self.__yaml, lambda: "30m")["resolver"]["defaults"]["exectimeout"]))
       
        return self._exec_timeout

    @property
    def default_tag(self):
        if not hasattr(self, "_default_tag"):
            self._default_tag =  str(ConfigProvider._navigate_or_else(self.__yaml, lambda: "default")["resolver"]["defaults"]["defaulttag"])
       
        return self._default_tag
    

    def __load_tag_config(self, tag):
        image_configs = ConfigProvider._navigate_or_else(self.__yaml, lambda: None)["resolver"]["images"]
        image_config = image_configs[tag]

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

        return ImageTagDefinition(image_config["container"],
                                  ConfigProvider._navigate_or_else(image_config, lambda: self.default_container_ttl)["containerttl"],
                                  ConfigProvider._navigate_or_else(image_config, lambda: self.default_exec_timeout)["exectimeout"],
                                  ConfigProvider._navigate_or_else(image_config, lambda: {})["execenv"],
                                  ConfigProvider._navigate_or_else(image_config, lambda: [])["execparams"],
                                  ConfigProvider._navigate_or_else(image_config, lambda: [])["envpropagate"])


    def container_data_of_tag(self, tag):
        if not tag in self.__tags.keys():
            self.__tags[tag] = self.__load_tag_config(tag)
        
        return self.__tags[tag]
     
  
