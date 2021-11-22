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

import RevitCommonAPI as com
import Result as res


# import Autodesk
from Autodesk.Revit.DB import *

class RevitWarningsSolverDuplicateMark:

    # class constructor taking two args:
    # filterFunc        a function to filter elements in warnings by
    # filterValues      a list containing the filter values
    def __init__(self, filterFunc, filterValues = []):
        '''constructor: this solver takes two arguments: a filter function and a list of values to filter by'''
        self.filter = filterFunc
        self.filterValues = filterValues

    # --------------------------- room tag not in room ---------------------------
    GUID = '6e1efefe-c8e0-483d-8482-150b9f1da21a'
    
    # doc       current drevit document
    # warnings  list of warnings
    def SolveWarnings(self, doc, warnings):
        '''solver setting element mark to nothing'''
        returnvalue = res.Result()
        for warning in warnings:
            elementIds = warning.GetFailingElements()
            for elid in elementIds:
                # check whether element passes filter
                if(self.filter(doc, elid, self.filterValues)):
                    element = doc.GetElement(elid)
                    #p = element.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
                    paras = element.GetOrderedParameters()
                    for p in paras:
                        if(p.Definition.BuiltInParameter == BuiltInParameter.ALL_MODEL_MARK):
                            result = com.setParameterValue(p, '', doc)
                            returnvalue.Update(result)
        return returnvalue
    
