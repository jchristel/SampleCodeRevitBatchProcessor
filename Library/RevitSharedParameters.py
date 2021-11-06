#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

import clr
import System

# import common library modules
import RevitCommonAPI as com
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_SHAREDPARAMETERS_HEADER = ['HOSTFILE', 'GUID', 'ID', 'NAME', 'PARAMETERBINDINGS']

# --------------------------------------------- utility functions ------------------

# returns all shared parameters in a model
# doc   current model document
def GetAllSharedParameters(doc):  
    collector = FilteredElementCollector(doc).OfClass(SharedParameterElement)
    return collector

# ------------------------------------------------------- parameter reporting --------------------------------------------------------------------

# returns all paramterbindings for a given parameter
# doc:              the current revit document
# paramName:        the parameter name
# paramType:        the parameter type
def ParamBindingExists(doc, paramName, paramType):
    categories = []
    map = doc.ParameterBindings
    iterator = map.ForwardIterator()
    iterator.Reset()
    while iterator.MoveNext():
        if iterator.Key != None and iterator.Key.Name == paramName and iterator.Key.ParameterType == paramType:
            elemBind = iterator.Current
            for cat in elemBind.Categories:
                categories.append(cat.Name)
            break
    return categories


# doc:              the current revit document
# revitFilePath:    fully qualified file path of Revit file
def GetSharedParameterReportData(doc, revitFilePath):
    '''gets shared parameter data ready for being printed to file'''
    data = []
    paras = GetAllSharedParameters(doc)
    for p in paras:
        pdef = p.GetDefinition()
        pbindings = []
        # parameter bindings do not exist in a family document
        if(doc.IsFamilyDocument == False):
            pbindings = ParamBindingExists(doc, Element.Name.GetValue(p), pdef.ParameterType)
        
        # just in case parameter name is not unicode
        parameterName = 'unknonw'
        try:   
            parameterName = util.EncodeAscii(Element.Name.GetValue(p))
        except Exception as ex:
            parameterName = 'Exception: ' + str(ex)
        # build data
        data.append([
            revitFilePath, 
            p.GuidValue.ToString(), 
            str(p.Id.IntegerValue), 
            parameterName,
            str(pbindings)
            ])
    return data