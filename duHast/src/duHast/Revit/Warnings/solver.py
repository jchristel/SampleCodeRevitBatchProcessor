"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Warnings solver utility class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import System
import clr

# from collections import namedtuple

from duHast.Utilities.Objects import result as res
from duHast.Revit.Warnings import warnings as rWar
from duHast.Revit.Warnings import solver_room_tag_to_room as rwsRoomTagToRoom
from duHast.Revit.Warnings import solver_duplicate_mark as rwsDuplicateMark

# import Autodesk
import Autodesk.Revit.DB as rdb

from duHast.Utilities.Objects import base

# a class used to return the value  if any, a message and the status of a method (true if everything is ok or false if something went wrong)
class RevitWarningsSolver(base.Base):

    # --------------------------- available filters ---------------------------

    def default_filter_return_all(self, doc, element_id):
        """
        Default filter for elements past into solver...returns True for any element past in.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param element_id: The id of the element to be checked.
        :type element_id: Autodesk.Revit.DB.ElementId

        :return: True always.
        :rtype: bool
        """
        return True

    # --------------------------- solvers initialise code ---------------------------

    #: default solver classes
    solver_room_tag_to_room = rwsRoomTagToRoom.RevitWarningsSolverRoomTagToRoom()
    solver_same_mark = rwsDuplicateMark.RevitWarningsSolverDuplicateMark(
        default_filter_return_all
    )

    #: solver dictionary of available warning solvers by guid
    AVAILABLE_SOLVERS = {
        solver_room_tag_to_room.GUID: solver_room_tag_to_room,
        solver_same_mark.GUID: solver_same_mark,
    }

    # --------------------------- solvers code ---------------------------

    def __init__(self):
        """
        Constructor: assigns the default element filter (pass all)
        """

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolver, self).__init__()

        self.filter_function_same_mark = self.default_filter_return_all

    def set_same_mark_filter_and_filter_solver(self, same_mark_filter_solver):
        """
        Method allowing to override the default filter function

        :param same_mark_filter_solver: A function to filter elements in warnings by
        :type same_mark_filter_solver: func(document, elementId, list of filter values)
        """

        # replace the old solver
        self.AVAILABLE_SOLVERS[same_mark_filter_solver.GUID] = same_mark_filter_solver
        self.solver_same_mark = same_mark_filter_solver

    def solve_warnings(self, doc):
        """
        Attempts to solve some warning in a revit model using available warnings solver.

        It will get all warnings in model, filter them by available solver GUIDs and finally will attempt to solve the warnings matched up with a solver.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return:
            Result class instance.

            - .result = True if all warnings could be solved. Otherwise False.
            - .message will contain all messages solver returned.

        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        try:
            for solver in self.AVAILABLE_SOLVERS:
                warnings = rWar.get_warnings_by_guid(
                    doc, self.AVAILABLE_SOLVERS[solver].GUID
                )
                result_solver = self.AVAILABLE_SOLVERS[solver].solve_warnings(
                    doc, warnings
                )
                return_value.update(result_solver)
        except Exception as e:
            print(str(e))
        return return_value
