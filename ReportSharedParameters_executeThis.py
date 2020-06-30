#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import clr
import System

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath_ = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_sharedPara.rvt'

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    revitFilePath_ = debugRevitFileName_

#set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)
#import common library
import Common
from Common import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

#build output file name
fileName_ = rootPath_ + '\\'+ GetOutPutFileName(revitFilePath_)

#returns all paramterbindings for a given parameter
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
            paramExists = True
            break
        else:
            paramExists = False
    return ('[' + str(','.join(categories)) + ']')

#method writing out shared parameter information
def writeSharedData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['GUID', 'ID', 'NAME', '\n']))
        for p in FilteredElementCollector(doc).OfClass(SharedParameterElement):
            pdef = p.GetDefinition()
            f.write('\t'.join([p.GuidValue.ToString(), str(p.Id.IntegerValue), EncodeAscii(Element.Name.GetValue(p)), ParamBindingExists(doc, Element.Name.GetValue(p), pdef.ParameterType), '\n']))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# -------------
# main:
# -------------

Output('Writing Shared Parameter Data.... start')

#write out shared parameter data
result_ = writeSharedData(doc, fileName_)

Output('Writing Shared Parameter Data.... status: ' + str(result_))
Output('Writing Shared Parameter Data.... finished ' + fileName_)
