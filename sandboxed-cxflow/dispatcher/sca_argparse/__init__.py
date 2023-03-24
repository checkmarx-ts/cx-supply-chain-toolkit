import re

class ScaArgsHandler:

    __r_cmd = "^-r|^--resolver-result-path"
    __s_cmd = "^-s|^--scan-path"
    __groups_fmt = "(?P<cmd>{cmd})=(?P<value>.+$)"
    __r_check = re.compile(__r_cmd)
    __s_check = re.compile(__s_cmd)
    __r_value_match = re.compile(__groups_fmt.format(cmd=__r_cmd))
    __s_value_match = re.compile(__groups_fmt.format(cmd=__s_cmd))

    # TODO: --cx* params are exploitable path params.  Currently these need to pass through
    # to SCAResolver since they need to be part of an online or offline scan.
    __pass_cmd = "^-p|^--password"
    __creds_cmd = "^-u|^--username|^-a|^--account|--server-url|^--authentication-server-url|^--sca-app-url"
    __creds_check = re.compile(f"{__pass_cmd}|{__creds_cmd}")
    __creds_match = re.compile(__groups_fmt.format(cmd=f"{__pass_cmd}|{__creds_cmd}"))

    __sensitive_cmd = f"^--proxies|^--cxpassword|{__pass_cmd}"
    __sensitive_check = re.compile(__sensitive_cmd)
    __sensitive_match = re.compile(__groups_fmt.format(cmd=__sensitive_cmd))
    

    @staticmethod
    def __filter_args(check_pattern, match_pattern, arg_array):
        ret = []
        delete = False

        for arg in arg_array:
            if delete:
                delete = False
                continue

            if not check_pattern.search(arg) is None:
                result = match_pattern.match(arg)
                if result is None:
                    delete = True
                continue
            else:
                ret.append(arg)
        
        return ret


    @staticmethod
    def _strip_creds(arg_array):
        return ScaArgsHandler.__filter_args(ScaArgsHandler.__creds_check, ScaArgsHandler.__creds_match, arg_array)

    @staticmethod
    def _strip_scan_inputs(arg_array):
        return ScaArgsHandler.__filter_args(ScaArgsHandler.__s_check, ScaArgsHandler.__s_value_match, arg_array)

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

    def __init__(self, args_array, operation=None):
        self.__op_args = args_array[2:]
        self._operation = args_array[1].lower() if operation is None else operation

        match self._operation:
            case "offline" | "online":
                self.__inpath_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__s_value_match, self.__op_args,
                                                               ScaArgsHandler.__find_match_index(ScaArgsHandler.__s_check, self.__op_args))

                self.__outpath_index  = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__r_value_match, self.__op_args,
                                                                 ScaArgsHandler.__find_match_index(ScaArgsHandler.__r_check, self.__op_args))
                self.__requires_tag_resolution = True

            case "upload":
                self.__inpath_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__r_value_match, self.__op_args,
                                                               ScaArgsHandler.__find_match_index(ScaArgsHandler.__r_check, self.__op_args))
                self.__outpath_index = None

                self.__requires_tag_resolution = False
            
            case _:
                raise Exception(f"Operation [{self._operation}] is unknown")

    def __get_operation(self):
        return self.__op
    
    def __set_operation(self, value):
        self.__op = value

    _operation = property(fget=__get_operation, fset=__set_operation)
    
    @property
    def can_two_stage(self):
        return self._operation == "online"
    
    @property
    def requires_tag_resolution(self):
        return self.__requires_tag_resolution
    
    @property
    def input_path(self):
        return self.__op_args[self.__inpath_index] if not self.__inpath_index is None else None
    
    @property
    def input_path_index(self):
        return self.__inpath_index if not self.__inpath_index is None else None

    @property
    def output_path(self):
        return self.__op_args[self.__outpath_index] if not self.__outpath_index is None else None

    @property
    def output_path_index(self):
        return self.__outpath_index if not self.__outpath_index is None else None
    
    def _clone_op_params(self):
        return self.__op_args.copy()
   
    def get_sanitized_param_string(self, param_array):
        p_copy = param_array.copy()
        for i in ScaArgsHandler.__find_match_indexes(ScaArgsHandler.__sensitive_check, p_copy):
            mask_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__sensitive_match, p_copy, i)
            p_copy[mask_index] = "MASKED"
        return p_copy

class OnlineOperation(ScaArgsHandler):
    def __init__(self, args_array, op="online"):
        super().__init__(args_array, op)

    def get_io_remapped_args(self, input_loc, output_loc):
        # TODO: handle cases when there is a file specified
        # TODO: optionally generate a unique filename
        params = self._clone_op_params()
        params[self.output_path_index] = output_loc
        params[self.input_path_index] = input_loc
        return [self._operation] + params


class OfflineOperation(OnlineOperation):
    def __init__(self, args_array, op="offline"):
        super().__init__(ScaArgsHandler._strip_creds(args_array), op)
    



class UploadOperation(ScaArgsHandler):
    def __init__(self, args_array):
        super().__init__(args_array, "upload")

    def get_remapped_args(self, input_loc):
        # TODO: handle cases when there is a file specified
        # TODO: optionally generate a unique filename
        params = self._clone_op_params()
        params[self.input_path_index] = input_loc
        return [self._operation] + ScaArgsHandler._strip_scan_inputs(params)


class PassthroughOperation(ScaArgsHandler):
    def __init__(self, args_array):
        super().__init__(args_array)

    def get_io_remapped_args(self, input_loc, output_loc):
        params = self._clone_op_params()
        if not self.output_path_index is None:
            params[self.output_path_index] = output_loc
        
        if not self.input_path_index is None:
            params[self.input_path_index] = input_loc
            
        return [self._operation] + params
