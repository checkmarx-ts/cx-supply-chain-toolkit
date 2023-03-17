import re

class ScaArgsHandler:

    __r_cmd = "^-r|^--resolver-result-path"
    __s_cmd = "^-s|^--scan-path"
    __groups_fmt = "(?P<cmd>{cmd})=(?P<value>.+$)"
    __r_check = re.compile(__r_cmd)
    __s_check = re.compile(__s_cmd)
    __r_value_match = re.compile(__groups_fmt.format(cmd=__r_cmd))
    __s_value_match = re.compile(__groups_fmt.format(cmd=__s_cmd))

    __sensitive_cmd = "^-p|^--password|^--proxies|^--cxpassword"
    __sensitive_check = re.compile(__sensitive_cmd)
    __sensitive_match = re.compile(__groups_fmt.format(cmd=__sensitive_cmd))
    
    @staticmethod
    def __find_match_index(checkspec, value_array):
        for v in value_array:
            if not checkspec.search(v) is None:
                return value_array.index(v)
        return None

    @staticmethod
    def __find_match_indexes(checkspec, value_array):
        ret = []
        for v in value_array:
            if not checkspec.search(v) is None:
                ret.append(value_array.index(v))
        return ret

    @staticmethod
    def __get_index_and_fix_params(match, param_array, param_index):
        result = match.match(param_array[param_index])
        if not result is None:
            result_dict = result.groupdict()
            param_array[param_index] = result_dict["cmd"]
            param_array.insert(param_index + 1, result_dict["value"])
        return param_index + 1

    def __init__(self, args_array):
        self.__passthru = args_array[2:]
        self.__operation = args_array[1]



        match self.__operation.lower():
            case "offline" | "online":
                self.__inpath_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__s_value_match, self.__passthru,
                                                               ScaArgsHandler.__find_match_index(ScaArgsHandler.__s_check, self.__passthru))

                self.__outpath_index  = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__r_value_match, self.__passthru,
                                                                 ScaArgsHandler.__find_match_index(ScaArgsHandler.__r_check, self.__passthru))
                
                self.__requires_tag_resolution = True

            case "upload":
                self.__inpath_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__r_value_match, self.__passthru,
                                                               ScaArgsHandler.__find_match_index(ScaArgsHandler.__r_check, self.__passthru))
                self.__outpath_index = None

                self.__requires_tag_resolution = False

    @property
    def requires_tag_resolution(self):
        return self.__requires_tag_resolution
    
    @property
    def input_path(self):
        return self.__passthru[self.__inpath_index] if not self.__inpath_index is None else None
    
    @property
    def input_path_index(self):
        return self.__inpath_index if not self.__inpath_index is None else None

    @property
    def output_path(self):
        return self.__passthru[self.__outpath_index] if not self.__outpath_index is None else None

    @property
    def output_path_index(self):
        return self.__outpath_index if not self.__inpath_index is None else None
    
    def get_modified_params(self, input_loc, output_loc=None):
        params = [self.__operation] + self.__passthru.copy()

        if not output_loc is None and not self.output_path_index is None:
            params[self.output_path_index] = output_loc

        params[self.input_path_index] = input_loc

        return params
    
    def get_orig_params(self):
        return [self.__operation] + self.__passthru.copy()
    
    def get_sanitized_param_string(self, param_array):
        p_copy = param_array.copy()
        for i in ScaArgsHandler.__find_match_indexes(ScaArgsHandler.__sensitive_check, p_copy):
            mask_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__sensitive_match, p_copy, i)
            p_copy[mask_index] = "MASKED"
        return p_copy

