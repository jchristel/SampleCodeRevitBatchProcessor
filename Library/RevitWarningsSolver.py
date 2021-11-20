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
from collections import namedtuple

import Result as res
import RevitRooms as rRoom
import RevitWarnings as rWar
import RevitCommonAPI as com

# import Autodesk
from Autodesk.Revit.DB import *

# a class used to return the value  if any, a message and the status of a method (true if everything is ok or false if something went wrong)
class RevitWarningsSolver:

    # --------------------------- available solvers ---------------------------

    # --------------------------- elements have duplicate mark values ---------------------------

    SOLVER_ELEMENT_DUPLICATE_MARK_GUID = '6e1efefe-c8e0-483d-8482-150b9f1da21a'

    # doc       current drevit document
    # warnings  list of warnings
    def SolverElementDuplicateMark(self, doc, warnings):
        '''solver setting element mark to nothing'''
        returnvalue = res.Result()
        for warning in warnings:
            elementIds = warning.GetFailingElements()
            for elid in elementIds:
                # check whether element passes filter
                if(self.filterFuncSameMark(doc, elid, self.filterValuesSameMark)):
                    element = doc.GetElement(elid)
                    p = element.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
                    #paras = element.GetOrderedParameters()
                    #for p in paras:
                        #if(p.Definition.BuiltInParameter == BuiltInParameter.ALL_MODEL_MARK):
                    result = com.setParameterValue(p,'',doc)
                    returnvalue.Update(result)
        return returnvalue

    # --------------------------- room tag not in room ---------------------------
    SOLVER_TAG_OUTSIDE_ROOM_GUID = '4f0bba25-e17f-480a-a763-d97d184be18a'
    
    # doc       current drevit document
    # warnings  list of warnings
    def SolverTagOutSideRoom(self, doc, warnings):
        '''solver moving room tags to room location point'''
        returnvalue = res.Result()
        for warning in warnings:
            elementIds = warning.GetFailingElements()
            for elid in elementIds:
                result = rRoom.MoveTagToRoom(doc, elid)
                returnvalue.Update(result)
        return  returnvalue 
    
    # --------------------------- solvers initialise code ---------------------------
    Solver = namedtuple("Solver", "guid function")

    solverRoomTag = Solver(SOLVER_TAG_OUTSIDE_ROOM_GUID, SolverTagOutSideRoom)
    solverDuplicateMark = Solver(SOLVER_ELEMENT_DUPLICATE_MARK_GUID, SolverElementDuplicateMark)

    AVAILABLE_SOLVERS = [
        solverRoomTag,
        solverDuplicateMark
    ]

    # --------------------------- solvers code ---------------------------

    def __init__(self): 
        self.filterFuncSameMark = self.DefaultFilterReturnAll
        self.filterValuesSameMark = []
    
    # doc   current model object
    def SolveWarnings(self,doc):
        '''attempts to solve some warning in a revit model'''
        returnvalue = res.Result()
        try:
            for solver in self.AVAILABLE_SOLVERS:
                warnings =  rWar.GetWarningsByGuid(doc, solver.guid)
                resultSolver = solver.function(doc, warnings)
                returnvalue.Update(resultSolver)
        except Exception as e:
            print (str(e))
        return returnvalue

    # doc           current model object
    # element       the elemet to be checked
    def DefaultFilterReturnAll(self, doc, elementId, **args):
        '''default filter for elements...returns True for any element passt in '''
        return True