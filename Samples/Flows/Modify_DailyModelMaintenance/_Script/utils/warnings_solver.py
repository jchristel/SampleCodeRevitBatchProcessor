"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing model warnings solver functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- same mark warning



"""

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
