# -*- coding: utf-8 -*-

import sys

import sollya

from sollya import S2, Interval, ceil, floor, round, inf, sup, log, exp, expm1, log2, guessdegree, dirtyinfnorm, RN, RD, cbrt
from sollya import parse as sollya_parse

from metalibm_core.core.attributes import ML_Debug
from metalibm_core.core.ml_operations import *
from metalibm_core.core.ml_formats import *
from metalibm_core.core.ml_table import ML_Table
from metalibm_core.code_generation.vhdl_backend import VHDLBackend
from metalibm_core.core.polynomials import *
from metalibm_core.core.ml_entity import ML_Entity, ML_EntityBasis, DefaultEntityArgTemplate
from metalibm_core.code_generation.generator_utility import FunctionOperator, FO_Result, FO_Arg


from metalibm_core.utility.ml_template import *
from metalibm_core.utility.log_report  import Log
from metalibm_core.utility.debug_utils import *
from metalibm_core.utility.num_utils   import ulp
from metalibm_core.utility.gappa_utils import is_gappa_installed


from metalibm_core.core.ml_hdl_format import *
from metalibm_core.core.ml_hdl_operations import *

class ML_LeadingZeroCounter(ML_Entity("ml_lzc")):
  @staticmethod
  def get_default_args(width = 32):
    return DefaultEntityArgTemplate( 
             precision = ML_Int32, 
             debug_flag = False, 
             target = VHDLBackend(), 
             output_file = "my_lzc.vhd", 
             entity_name = "my_lzc",
             language = VHDL_Code,
             width = width,
           )

  def __init__(self, arg_template = None):
    # building default arg_template if necessary
    arg_template = ML_LeadingZeroCounter.get_default_args() if arg_template is None else arg_template
    # initializing I/O precision
    self.width = arg_template.width
    precision = arg_template.precision
    io_precisions = [precision] * 2
    Log.report(Log.Info, "generating LZC with width={}".format(self.width))

    # initializing base class
    ML_EntityBasis.__init__(self, 
      base_name = "ml_lzc",
      arg_template = arg_template
    )

    self.accuracy  = arg_template.accuracy
    self.precision = arg_template.precision

  def generate_scheme(self):
    lzc_width = int(ceil(log2(self.width)))
    Log.report(Log.Info, "width of lzc out is {}".format(lzc_width))
    input_precision = ML_StdLogicVectorFormat(self.width)
    precision = ML_StdLogicVectorFormat(lzc_width)
    # declaring main input variable
    vx = self.implementation.add_input_signal("x", input_precision) 
    vr_out = Signal("lzc", precision = precision, var_type = Variable.Local)
    iterator = Variable("i", precision = ML_Integer, var_type = Variable.Local)
    lzc_loop = RangeLoop(
      iterator, 
      Interval(0, self.width - 1),
      ConditionBlock(
        Comparison(
          VectorElementSelection(vx, iterator, precision = ML_StdLogic),
          Constant(1, precision = ML_StdLogic),
          specifier = Comparison.Equal,
          precision = ML_Bool
        ),
        ReferenceAssign(
          vr_out, 
          Conversion(
            Subtraction(
              Constant(self.width - 1, precision = ML_Integer),
              iterator, 
              precision = ML_Integer
            ),
          precision = precision),
        )
      ),
      specifier = RangeLoop.Increasing,
    )
    lzc_process = Process(
      Statement(
        ReferenceAssign(vr_out, Constant(self.width, precision = precision)),
        lzc_loop, 
      ),
      sensibility_list = [vx]
    )

    self.implementation.add_process(lzc_process)
    

    self.implementation.add_output_signal("vr_out", vr_out)

    return [self.implementation]

  standard_test_cases =[sollya_parse(x) for x in  ["1.1", "1.5"]]


if __name__ == "__main__":
    # auto-test
    arg_template = ML_EntityArgTemplate(default_entity_name = "new_lzc", default_output_file = "ml_lzc.vhd")
    arg_template.parser.add_argument("--width", dest = "width", type=int, default = ArgDefault(32), help = "set input width value (in bits)")
    # argument extraction 
    args = parse_arg_index_list = arg_template.arg_extraction()

    ml_lzc           = ML_LeadingZeroCounter(args)

    ml_lzc.gen_implementation()
