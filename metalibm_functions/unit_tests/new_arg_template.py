# -*- coding: utf-8 -*-

import sys

from sollya import *

from metalibm_core.core.ml_function import ML_Function, ML_FunctionBasis

from metalibm_core.core.attributes import ML_Debug
from metalibm_core.core.ml_operations import *

from metalibm_core.core.ml_formats import *
from metalibm_core.core.ml_complex_formats import * 

from metalibm_core.code_generation.c_code_generator import CCodeGenerator
from metalibm_core.code_generation.generic_processor import GenericProcessor
from metalibm_core.code_generation.mpfr_backend import MPFRProcessor
from metalibm_core.code_generation.code_object import CodeObject
from metalibm_core.code_generation.code_function import CodeFunction
from metalibm_core.code_generation.code_constant import C_Code 
from metalibm_core.core.ml_optimization_engine import OptimizationEngine
from metalibm_core.core.polynomials import *
from metalibm_core.core.ml_table import ML_Table

from metalibm_core.code_generation.gappa_code_generator import GappaCodeGenerator

from metalibm_core.utility.gappa_utils import execute_gappa_script_extract
from metalibm_core.utility.ml_template import *

from metalibm_core.utility.arg_utils import test_flag_option, extract_option_value  

from metalibm_core.utility.debug_utils import * 

class ML_UT_NewArgTemplate(ML_Function("ml_ut_new_arg_template")):
  def __init__(self, 
                 arg_template,
                 precision = ML_Binary32, 
                 abs_accuracy = S2**-24, 
                 libm_compliant = True, 
                 debug_flag = False, 
                 fuse_fma = True, 
                 fast_path_extract = True,
                 target = MPFRProcessor(), 
                 output_file = "ut_new_arg_template.c", 
                 function_name = "ut_new_arg_template",
                 auto_test = False):
    precision = ArgDefault.select_value([arg_template.precision, precision])
    io_precisions = [precision] * 2
    print "arg_template: ", arg_template

    # initializing base class
    ML_FunctionBasis.__init__(self, 
      base_name = "ut_new_arg_template",
      function_name = function_name,
      output_file = output_file,

      io_precisions = io_precisions,
      abs_accuracy = None,
      libm_compliant = libm_compliant,

      processor = target,
      fuse_fma = fuse_fma,
      fast_path_extract = fast_path_extract,

      arg_template = arg_template,

      debug_flag = debug_flag
    )

    self.precision = precision

  def numeric_emulate(self, input_value):
    return input_value + input_value * input_value


  def generate_scheme(self):
    #func_implementation = CodeFunction(self.function_name, output_format = self.precision)
    vx = self.implementation.add_input_variable("x", self.precision)

    scheme = Statement(Return(vx + vx * vx ))

    return scheme

if __name__ == "__main__":
  # auto-test
  #arg_template = ML_ArgTemplate(default_function_name = "new_ut_new_arg_template", default_output_file = "new_ut_new_arg_template.c" )
  #arg_template.sys_arg_extraction()
  arg_template = ML_NewArgTemplate("new_ut_new_arg_template")
  args = arg_template.arg_extraction()

  ml_ut_new_arg_template = ML_UT_NewArgTemplate(args)
  ml_ut_new_arg_template.gen_implementation(display_after_gen = True, display_after_opt = True)
