import unittest
import sca_argparse

class sca_argparse_tests(unittest.TestCase):

    __inpath = "input"
    __outpath = "output"
    __mod_inpath = "mod/input"
    __mod_outpath = "mod/output"

    
    def test_canary(self):
        self.assertTrue(True)

    def test_offline_identifies_input_path_short(self):
        o = sca_argparse.ScaArgsHandler(["", "offline", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        self.assertEqual(o.input_path, sca_argparse_tests.__inpath)

    def test_offline_identifies_input_path_long(self):
        o = sca_argparse.ScaArgsHandler(["", "offline", "--scan-path", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        self.assertEqual(o.input_path, sca_argparse_tests.__inpath)

    def test_offline_identifies_output_path_short(self):
        o = sca_argparse.ScaArgsHandler(["", "offline", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        self.assertEqual(o.output_path, sca_argparse_tests.__outpath)

    def test_offline_identifies_output_path_long(self):
        o = sca_argparse.ScaArgsHandler(["", "offline", "-s", sca_argparse_tests.__inpath, "--resolver-result-path", sca_argparse_tests.__outpath])
        self.assertEqual(o.output_path, sca_argparse_tests.__outpath)



    def test_online_identifies_input_path_short(self):
        o = sca_argparse.ScaArgsHandler(["", "online", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        self.assertEqual(o.input_path, sca_argparse_tests.__inpath)

    def test_online_identifies_input_path_long(self):
        o = sca_argparse.ScaArgsHandler(["", "online", "--scan-path", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        self.assertEqual(o.input_path, sca_argparse_tests.__inpath)

    def test_online_identifies_output_path_short(self):
        o = sca_argparse.ScaArgsHandler(["", "online", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        self.assertEqual(o.output_path, sca_argparse_tests.__outpath)

    def test_online_identifies_output_path_long(self):
        o = sca_argparse.ScaArgsHandler(["", "online", "-s", sca_argparse_tests.__inpath, "--resolver-result-path", sca_argparse_tests.__outpath])
        self.assertEqual(o.output_path, sca_argparse_tests.__outpath)



    def test_upload_identifies_input_path_short(self):
        o = sca_argparse.ScaArgsHandler(["", "upload", "-r", sca_argparse_tests.__inpath])
        self.assertEqual(o.input_path, sca_argparse_tests.__inpath)

    def test_upload_identifies_input_path_long(self):
        o = sca_argparse.ScaArgsHandler(["", "upload", "--resolver-result-path", sca_argparse_tests.__inpath])
        self.assertEqual(o.input_path, sca_argparse_tests.__inpath)

    def test_upload_no_output_path_short(self):
        o = sca_argparse.ScaArgsHandler(["", "upload", "-r", sca_argparse_tests.__inpath])
        self.assertIsNone(o.output_path)

    def test_upload_no_output_path_long(self):
        o = sca_argparse.ScaArgsHandler(["", "upload", "--resolver-result-path", sca_argparse_tests.__inpath])
        self.assertIsNone(o.output_path)


    def test_offline_input_param_modified_short(self):
        o = sca_argparse.OfflineOperation(["", "offline", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.input_path_index, mod[1:].index(sca_argparse_tests.__mod_inpath))

    def test_offline_input_param_modified_long(self):
        o = sca_argparse.OfflineOperation(["", "offline", "-s", sca_argparse_tests.__inpath, "--resolver-result-path", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.input_path_index, mod[1:].index(sca_argparse_tests.__mod_inpath))

    def test_offline_output_param_modified_short(self):
        o = sca_argparse.OfflineOperation(["", "offline", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.output_path_index, mod[1:].index(sca_argparse_tests.__mod_outpath))

    def test_offline_output_param_modified_long(self):
        o = sca_argparse.OfflineOperation(["", "offline", "--scan-path", sca_argparse_tests.__inpath, "--resolver-result-path", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.output_path_index, mod[1:].index(sca_argparse_tests.__mod_outpath))


    def test_online_input_param_modified_short(self):
        o = sca_argparse.OnlineOperation(["", "online", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.input_path_index, mod[1:].index(sca_argparse_tests.__mod_inpath))

    def test_online_input_param_modified_long(self):
        o = sca_argparse.OnlineOperation(["", "online", "-s", sca_argparse_tests.__inpath, "--resolver-result-path", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.input_path_index, mod[1:].index(sca_argparse_tests.__mod_inpath))

    def test_online_output_param_modified_short(self):
        o = sca_argparse.OnlineOperation(["", "online", "-s", sca_argparse_tests.__inpath, "-r", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.output_path_index, mod[1:].index(sca_argparse_tests.__mod_outpath))

    def test_online_output_param_modified_long(self):
        o = sca_argparse.OnlineOperation(["", "online", "--scan-path", sca_argparse_tests.__inpath, "--resolver-result-path", sca_argparse_tests.__outpath])
        mod = o.get_io_remapped_args(sca_argparse_tests.__mod_inpath, sca_argparse_tests.__mod_outpath)
        self.assertEqual(o.output_path_index, mod[1:].index(sca_argparse_tests.__mod_outpath))




    def test_upload_input_param_modified_short(self):
        o = sca_argparse.UploadOperation(["", "upload", "-r", sca_argparse_tests.__inpath])
        mod = o.get_remapped_args(sca_argparse_tests.__mod_inpath)
        self.assertEqual(o.input_path_index, mod[1:].index(sca_argparse_tests.__mod_inpath))

    def test_upload_input_param_modified_long(self):
        o = sca_argparse.UploadOperation(["", "upload", "--resolver-result-path", sca_argparse_tests.__inpath])
        mod = o.get_remapped_args(sca_argparse_tests.__mod_inpath)
        self.assertEqual(o.input_path_index, mod[1:].index(sca_argparse_tests.__mod_inpath))

    def test_upload_output_param_none_short(self):
        o = sca_argparse.UploadOperation(["", "upload", "-r", sca_argparse_tests.__inpath])
        mod = o.get_remapped_args(sca_argparse_tests.__mod_inpath)
        self.assertIsNone(o.output_path)

    def test_upload_output_param_none_long(self):
        o = sca_argparse.UploadOperation(["", "upload", "--resolver-result-path", sca_argparse_tests.__inpath])
        mod = o.get_remapped_args(sca_argparse_tests.__mod_inpath)
        self.assertIsNone(o.output_path)


