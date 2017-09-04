# -*- coding: utf-8 -*-

""" Adaptative fixed-point size unit test """

import sollya

from sollya import parse as sollya_parse

from metalibm_core.core.ml_operations import (
    Comparison, Addition, Select, Constant, Conversion,
    Min, Max,
    Statement
)
from metalibm_core.code_generation.code_constant import VHDL_Code
from metalibm_core.core.ml_formats import (
    ML_Int32
)
from metalibm_core.code_generation.vhdl_backend import VHDLBackend
from metalibm_core.core.ml_entity import (
    ML_Entity, ML_EntityBasis, DefaultEntityArgTemplate
)
from metalibm_core.utility.ml_template import \
    ML_EntityArgTemplate
from metalibm_core.utility.log_report import Log
from metalibm_core.core.ml_hdl_format import fixed_point

from metalibm_functions.unit_tests.utils import TestRunner

from metalibm_core.opt.p_check_precision import Pass_CheckGeneric
from metalibm_core.core.passes import PassScheduler


from metalibm_core.utility.rtl_debug_utils import (
    debug_std, debug_dec, debug_fixed
)


class PipelinedBench(ML_Entity("ut_pipelined_bench_entity"), TestRunner):
    """ Adaptative Entity unit-test """
    @staticmethod
    def get_default_args(width=32, **kw):
        """ generate default argument template """
        return DefaultEntityArgTemplate(
            precision=ML_Int32,
            debug_flag=False,
            target=VHDLBackend(),
            output_file="my_adapative_entity.vhd",
            entity_name="my_adaptative_entity",
            language=VHDL_Code,
            width=width,
            passes=[
                ("beforepipelining:dump_with_stages"),
                ("beforepipelining:size_datapath"),
                ("beforepipelining:dump_with_stages"),
                ("beforepipelining:rtl_legalize"),
                ("beforepipelining:dump_with_stages"),
                ("beforepipelining:unify_pipeline_stages"),
                ("beforepipelining:dump_with_stages"),
                ],
        )

    def __init__(self, arg_template=None):
        """ Initialize """
        # building default arg_template if necessary
        arg_template = PipelinedBench.get_default_args() if \
            arg_template is None else arg_template
        # initializing I/O precision
        self.width = arg_template.width
        precision = arg_template.precision
        io_precisions = [precision] * 2
        Log.report(
            Log.Info,
            "generating Adaptative Entity with width={}".format(self.width)
        )

        # initializing base class
        ML_EntityBasis.__init__(self,
                                base_name="adaptative_design",
                                arg_template=arg_template
                                )

        self.accuracy = arg_template.accuracy
        self.precision = arg_template.precision

        int_size = 3
        frac_size = 7

        self.input_precision = fixed_point(int_size, frac_size)
        self.output_precision = fixed_point(int_size, frac_size)


    def generate_scheme(self):
        """ main scheme generation """
        Log.report(Log.Info, "input_precision is {}".format(self.input_precision))
        Log.report(Log.Info, "output_precision is {}".format(self.output_precision))

        # declaring main input variable
        var_x = self.implementation.add_input_signal("x", self.input_precision)
        var_y = self.implementation.add_input_signal("y", self.input_precision)
        var_x.set_attributes(debug = debug_fixed)
        var_y.set_attributes(debug = debug_fixed)

        self.implementation.start_new_stage()

        add = var_x + var_y

        self.implementation.start_new_stage()

        sub = add - var_y

        self.implementation.start_new_stage()

        pre_result = sub - var_x

        self.implementation.start_new_stage()

        post_result = pre_result + var_x

        result = Conversion(pre_result, precision=self.output_precision)

        self.implementation.add_output_signal("vr_out", result)

        return [self.implementation]

    standard_test_cases = [
    ]

    def numeric_emulate(self, io_map):
        """ Meta-Function numeric emulation """
        vx = io_map["x"]
        vy = io_map["y"]
        result = {"vr_out": vx}
        return result


    @staticmethod
    def __call__(args):
        # just ignore args here and trust default constructor?
        # seems like a bad idea.
        ut_adaptative_entity = PipelinedBench(args)
        ut_adaptative_entity.gen_implementation()
        return True

run_test = PipelinedBench


if __name__ == "__main__":
        # auto-test
    main_arg_template = ML_EntityArgTemplate(
        default_entity_name="ut_pipelined_bench_entity",
        default_output_file="ut_pipelined_bench_entity.vhd",
        default_arg=PipelinedBench.get_default_args()
    )
    main_arg_template.parser.add_argument(
        "--width", dest="width", type=int, default=32,
        help="set input width value (in bits)"
    )
    # argument extraction
    args = parse_arg_index_list = main_arg_template.arg_extraction()

    ut_pipelined_bench = PipelinedBench(args)

    ut_pipelined_bench.gen_implementation()
