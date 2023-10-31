"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing model warnings solver functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- same mark warning



"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import os

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Revit.Warnings.solver import RevitWarningsSolver
from cleanup_actions import CUSTOM_DUPLICATE_MARK_SOLVER

# ----------------------------------------------- warnings related code -----------------------------------------


def solve_warnings(doc, revit_file_path, output):
    """
    Automatic warnings solver

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified file of the model.
    :type revit_file_path: str

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Fixing warnings...start")
    solver = RevitWarningsSolver()

    # over write the default duplicate mark solver
    solver.set_same_mark_filter_and_filter_solver(CUSTOM_DUPLICATE_MARK_SOLVER)

    # fix warnings
    task_value = solver.solve_warnings(doc)
    return_value.update(task_value)
    return return_value
