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

import Result as res
import RevitWarnings as rWar

import RevitWarningsSolverRoomTagToRoom as rwsRoomTagToRoom
import RevitWarningsSolverDuplicateMark as rwsDuplicateMark

# import Autodesk
from Autodesk.Revit.DB import *

# a class used to return the value  if any, a message and the status of a method (true if everything is ok or false if something went wrong)
class RevitWarningsSolver:

    # --------------------------- available solvers ---------------------------

    # doc           current model object
    # element       the elemet to be checked
    def DefaultFilterReturnAll(self, doc, elementId):
        '''default filter for elements...returns True for any element passt in '''
        return True
    
    # --------------------------- solvers initialise code ---------------------------
    # named tuple format used in list
    #Solver = namedtuple("Solver", "guid function")

    # default solver classes
    solveRoomTagToRoom = rwsRoomTagToRoom.RevitWarningsSolverRoomTagToRoom()
    solverSameMark = rwsDuplicateMark.RevitWarningsSolverDuplicateMark(DefaultFilterReturnAll)
    
    # solver tuple list of available warning solvers
    #solverRoomTag = Solver(solveRoomTagToRoom.SOLVER_TAG_OUTSIDE_ROOM_GUID, rwsRoomTagToRoom.RevitWarningsSolverRoomTagToRoom())
    #solverDuplicateMark = Solver(SOLVER_ELEMENT_DUPLICATE_MARK_GUID, SolverElementDuplicateMark)

    AVAILABLE_SOLVERS = {
        solveRoomTagToRoom.GUID:solveRoomTagToRoom,
        solverSameMark.GUID:solverSameMark
    }

    # --------------------------- solvers code ---------------------------

    def __init__(self): 
        self.filterFuncSameMark = self.DefaultFilterReturnAll
    
    # sameMarkFilterFunction        function to be used to filter elements
    # sameMarkFilterValuee          list of filter values used by filter function
    def SetSameMarkFilterAndFilterSolver(self, sameMarkFilterSolver):
        '''over rides default same mark filter class'''
        # replace the old solver
        self.AVAILABLE_SOLVERS[sameMarkFilterSolver.GUID] = sameMarkFilterSolver
        self.solverSameMark = sameMarkFilterSolver

    # doc   current model object
    def SolveWarnings(self,doc):
        '''attempts to solve some warning in a revit model'''
        returnvalue = res.Result()
        try:
            for solver in self.AVAILABLE_SOLVERS:
                warnings =  rWar.GetWarningsByGuid(doc, self.AVAILABLE_SOLVERS[solver].GUID)
                resultSolver = self.AVAILABLE_SOLVERS[solver].SolveWarnings(doc, warnings)
                returnvalue.Update(resultSolver)
        except Exception as e:
            print (str(e))
        return returnvalue

    