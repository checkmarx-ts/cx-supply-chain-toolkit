import re

class ScaArgsHandler:

    __r_cmd = "^-r|^--resolver-result-path"
    __s_cmd = "^-s|^--scan-path"
    __groups_fmt = "(?P<cmd>{cmd})=(?P<value>.+$)"
    __r_check = re.compile(__r_cmd)
    __s_check = re.compile(__s_cmd)
    __r_value_match = re.compile(__groups_fmt.format(cmd=__r_cmd))
    __s_value_match = re.compile(__groups_fmt.format(cmd=__s_cmd))
    
    @staticmethod
    def __find_match_index(matchspec, value_array):
        for v in value_array:
            if not matchspec.search(v) is None:
                return value_array.index(v)
        return None

    def __init__(self, args_array):
        self.__passthru = args_array[2:]
        self.__operation = args_array[1]

        def get_index_and_fix_params(match, passthru_index):
            result = match.match(self.__passthru[passthru_index])
            if not result is None:
                result_dict = result.groupdict()
                self.__passthru[passthru_index] = result_dict["cmd"]
                self.__passthru.insert(passthru_index + 1, result_dict["value"])
            return passthru_index + 1


        match self.__operation.lower():
            case "offline" | "online":
                i_index = ScaArgsHandler.__find_match_index(ScaArgsHandler.__s_check, self.__passthru)
                self.__inpath_index = get_index_and_fix_params(ScaArgsHandler.__s_value_match, 
                                                               ScaArgsHandler.__find_match_index(ScaArgsHandler.__s_check, self.__passthru))

                self.__outpath_index  = get_index_and_fix_params(ScaArgsHandler.__r_value_match, 
                                                                 ScaArgsHandler.__find_match_index(ScaArgsHandler.__r_check, self.__passthru))

            case "upload":
                self.__inpath_index = get_index_and_fix_params(ScaArgsHandler.__r_value_match, 
                                                               ScaArgsHandler.__find_match_index(ScaArgsHandler.__r_check, self.__passthru))
                self.__outpath_index = None
        pass

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

