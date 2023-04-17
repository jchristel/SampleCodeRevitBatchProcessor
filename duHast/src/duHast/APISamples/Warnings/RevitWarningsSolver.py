'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Warnings solver utility class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import System
import clr
#from collections import namedtuple

from duHast.Utilities import Result as res
from duHast.APISamples.Warnings import RevitWarnings as rWar
from duHast.APISamples.Warnings import RevitWarningsSolverRoomTagToRoom as rwsRoomTagToRoom
from duHast.APISamples.Warnings import RevitWarningsSolverDuplicateMark as rwsDuplicateMark

# import Autodesk
import Autodesk.Revit.DB as rdb

from duHast.Utilities import Base

# a class used to return the value  if any, a message and the status of a method (true if everything is ok or false if something went wrong)
class RevitWarningsSolver(Base.Base):

    # --------------------------- available filters ---------------------------

    def default_filter_return_all(self, doc, elementId):
        '''
        Default filter for elements past into solver...returns True for any element past in.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param elementId: The id of the element to be checked.
        :type elementId: Autodesk.Revit.DB.ElementId
        
        :return: True always.
        :rtype: bool
        '''
        return True
    
    # --------------------------- solvers initialise code ---------------------------
    
    #: default solver classes
    solver_room_tag_to_room = rwsRoomTagToRoom.RevitWarningsSolverRoomTagToRoom()
    solver_same_mark = rwsDuplicateMark.RevitWarningsSolverDuplicateMark(default_filter_return_all)
    
    #: solver dictionary of available warning solvers by guid 
    AVAILABLE_SOLVERS = {
        solver_room_tag_to_room.GUID:solver_room_tag_to_room,
        solver_same_mark.GUID:solver_same_mark
    }

    # --------------------------- solvers code ---------------------------

    def __init__(self): 
        '''
        Constructor: assigns the default element filter (pass all) 
        '''

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolver, self).__init__() 

        self.filterFuncSameMark = self.default_filter_return_all
    
    def set_same_mark_filter_and_filter_solver(self, sameMarkFilterSolver):
        '''
        Method allowing to override the default filter function

        :param sameMarkFilterSolver: A function to filter elements in warnings by
        :type sameMarkFilterSolver: func(document, elementId, list of filter values)
        '''

        # replace the old solver
        self.AVAILABLE_SOLVERS[sameMarkFilterSolver.GUID] = sameMarkFilterSolver
        self.solver_same_mark = sameMarkFilterSolver

    def solve_warnings(self,doc):
        '''
        Attempts to solve some warning in a revit model using available warnings solver.

        It will get all warnings in model, filter them by available solver GUIDs and finally will attempt to solve the warnings matched up with a solver.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return: 
            Result class instance.
            
            - .result = True if all warnings could be solved. Otherwise False.
            - .message will contain all messages solver returned.
        
        :rtype: :class:`.Result`
        '''

        returnValue = res.Result()
        try:
            for solver in self.AVAILABLE_SOLVERS:
                warnings =  rWar.get_warnings_by_guid(doc, self.AVAILABLE_SOLVERS[solver].GUID)
                resultSolver = self.AVAILABLE_SOLVERS[solver].SolveWarnings(doc, warnings)
                returnValue.Update(resultSolver)
        except Exception as e:
            print (str(e))
        return returnValue

    