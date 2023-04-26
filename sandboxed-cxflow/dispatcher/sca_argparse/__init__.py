import re, uuid, os
from pathlib import Path
import tempfile

class ScaArgsHandler:

    __r_cmd = "^-r|^--resolver-result-path"
    __s_cmd = "^-s|^--scan-path"
    __groups_fmt = "(?P<cmd>{cmd})=(?P<value>.+$)"
    __r_check = re.compile(__r_cmd)
    __s_check = re.compile(__s_cmd)
    __r_value_match = re.compile(__groups_fmt.format(cmd=__r_cmd))
    __s_value_match = re.compile(__groups_fmt.format(cmd=__s_cmd))

    __pass_cmd = "^-p|^--password"
    __creds_cmd = "^-u|^--username|^-a|^--account|--server-url|^--authentication-server-url|^--sca-app-url"
    __creds_check = re.compile(f"{__pass_cmd}|{__creds_cmd}")
    __creds_match = re.compile(__groups_fmt.format(cmd=f"{__pass_cmd}|{__creds_cmd}"))

    __sensitive_cmd = f"^--proxies|^--cxpassword|{__pass_cmd}"
    __sensitive_check = re.compile(__sensitive_cmd)
    __sensitive_match = re.compile(__groups_fmt.format(cmd=__sensitive_cmd))

    __report_path_cmd = "^--report-path"
    __report_path_check = re.compile(__report_path_cmd)
    __report_path_match = re.compile(__groups_fmt.format(cmd=__report_path_cmd))
    __report_all_cmd = "^--report-.*"
    __report_cmd_check = re.compile(__report_all_cmd)
    __report_cmd_match = re.compile(__groups_fmt.format(cmd=__report_all_cmd))
    

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
    def _strip_report_args(arg_array):
        return ScaArgsHandler.__filter_args(ScaArgsHandler.__report_cmd_check, ScaArgsHandler.__report_cmd_match, arg_array)

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
        
        if param_index is None or param_array is None:
            return None
        
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
        
        self.__reportpath_index =  ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__report_path_match, self.__op_args,
                                                                 ScaArgsHandler.__find_match_index(ScaArgsHandler.__report_path_check, self.__op_args))
    def __get_operation(self):
        return self.__op
    
    def __set_operation(self, value):
        self.__op = value

    _operation = property(fget=__get_operation, fset=__set_operation)

    @property
    def operation(self):
        return self._operation
    
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
    

    def _set_results_path_for_output(self, value):
        if self.__outpath_index is None:
            self.__op_args.append ("-r")
            self.__op_args.append(value)
            self.__outpath_index = len(self.__op_args) - 1
        else:
            self.__op_args[self.__outpath_index] = value

    def _set_results_path_for_input(self, value):
        if self.__inpath_index is None:
            self.__op_args.append ("-r")
            self.__op_args.append(value)
            self.__inpath_index = len(self.__op_args) - 1
        else:
            self.__op_args[self.__inpath_index] = value


    @property
    def output_path_index(self):
        return self.__outpath_index if not self.__outpath_index is None else None


    @property
    def report_path_index(self):
        return self.__reportpath_index if not self.__reportpath_index is None else None

    @property
    def report_path(self):
        return self.__op_args[self.__reportpath_index] if not self.__reportpath_index is None else None
    
    def _clone_op_params(self):
        return self.__op_args.copy()
   
    def get_sanitized_param_string(self, param_array):
        p_copy = param_array.copy()
        for i in ScaArgsHandler.__find_match_indexes(ScaArgsHandler.__sensitive_check, p_copy):
            mask_index = ScaArgsHandler.__get_index_and_fix_params(ScaArgsHandler.__sensitive_match, p_copy, i)
            p_copy[mask_index] = "MASKED"
        return p_copy

class IOOperation(ScaArgsHandler):
    def __init__(self, args_array, op=None):
        super().__init__(args_array, op)
        pass

    @staticmethod
    def remap_path(orig_path, desired_path):
        parsed_path = Path(orig_path)
        if len(parsed_path.suffix) > 0:
            return Path(desired_path) / parsed_path.name
        else:
            return desired_path


    def get_io_remapped_args(self, input_loc, output_loc, report_loc=None):
        params = self._clone_op_params()

        if not self.output_path_index is None:
            params[self.output_path_index] = IOOperation.remap_path(params[self.output_path_index], output_loc)

        if not self.input_path_index is None:
            params[self.input_path_index] = IOOperation.remap_path(params[self.input_path_index], input_loc)

        if not report_loc is None and not self.report_path_index is None:
            params[self.report_path_index] = IOOperation.remap_path(params[self.report_path_index], report_loc)

        return [self._operation] + params


class OnlineOperation(IOOperation):
    def __init__(self, args_array, op="online"):
        super().__init__(args_array, op)


class OfflineOperation(OnlineOperation):
    def __init__(self, args_array, op="offline"):
        super().__init__(ScaArgsHandler._strip_creds(args_array), op)
        self.__out_filename = None
        self.__should_delete = False
        
        if self.output_path_index is None:
            self._set_results_path_for_output(tempfile.gettempdir())

    def get_io_remapped_args(self, input_loc, output_loc):
        parsed_outpath = Path(output_loc)
        if not len(parsed_outpath.suffix) > 0:
            self.__out_filename = f"{str(uuid.uuid4())}.json"
            parsed_outpath /= self.__out_filename
            self.__should_delete = True
        else:
            self.__out_filename = parsed_outpath.name

        return ScaArgsHandler._strip_report_args(super().get_io_remapped_args(input_loc, str(parsed_outpath)))
    
    def __del__(self):
        if self.__should_delete and not self.__out_filename is None:
            outfile = Path(self.output_path) / self.__out_filename
            if os.path.exists(outfile):
                os.remove(outfile)
            

    @property
    def out_filename(self):
        return self.__out_filename

    @property
    def should_delete(self):
        return self.__should_delete


class UploadOperation(IOOperation):
    def __init__(self, args_array):
        super().__init__(args_array, "upload")

        if self.input_path_index is None:
            self._set_results_path_for_input(tempfile.gettempdir())

    def get_io_remapped_args(self, input_loc, output_loc, report_loc, in_filename):
        params = self._clone_op_params()

        if not self.input_path_index is None:
            parsed_inpath = Path(input_loc)
            
            if len(parsed_inpath.suffix) == 0:
                parsed_inpath /= in_filename
                params[self.input_path_index] = IOOperation.remap_path(params[self.input_path_index], str(parsed_inpath))

        return ScaArgsHandler._strip_scan_inputs(super().get_io_remapped_args(params[self.input_path_index], output_loc, report_loc))


class PassthroughOperation(IOOperation):
    def __init__(self, args_array):
        super().__init__(args_array)
