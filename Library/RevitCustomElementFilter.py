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

class RevitCustomElementFilter:

    # class constructor taking two args:
    # elementFilters            list of methods which accept as arguments the current document, and the element id of the element to check
    # isLogicalANDFilter        if True this acts like and AND: all filters must return True in order to return true overall, if false this acts like an ORL just one of the filters need to return true
    #                           to return True overall
    def __init__(self, elementFilters = [] , isLogicalANDFilter = True):
        '''constructor: this takes a list of element filters and a flag whether it is a logical AND filter (default)'''
        self.elementFilters = elementFilters
        self.isLogicalANDFilter = isLogicalANDFilter
    

    # doc           current drevit document
    # elementId     revit element id
    def CheckElement(self, doc, elementId):
        '''filter checking whether element meets criteria'''
        if(self.isLogicalANDFilter):
            filterOverAll = True
        else:
            filterOverAll = False
        
        for filter in self.elementFilters:
            filterResult = filter(doc, elementId)
            if(self.isLogicalANDFilter == False and filterResult == True):
                filterOverAll = True
                # can leave the loop at this point since only one of the tests need to result true in OR filter mode
                break
            elif(self.isLogicalANDFilter == True and filterResult == False):
                filterOverAll = False
                # can leave the loop at this point since only one of the tests need to result false in AND filter mode
                break
            else:
                filterOverAll = filterOverAll and filterResult
        return filterOverAll
