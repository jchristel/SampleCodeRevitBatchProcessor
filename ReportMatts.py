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

# sample description
# how to report on materials

import clr
import System

# flag whether this runs in debug or not
debug_ = False

# --------------------------
# default file path locations
# --------------------------
# store output here:
rootPath_ = r'C:\temp'
# path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_mats.rvt'

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    revitFilePath_ = debugRevitFileName_

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

# import common library
import Utility as util

from Autodesk.Revit.DB import *

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------
def WriteType (action, description, fileName, doc):
    status = True
    collector = action()
    Output ('Writing ' + description +'....')
    f = open(fileName, 'w')
    f.write('\t'.join(['HOSTFILE', 'ID', 'MATERIALNAME', 'PARAMETERNAME', 'PARAMETERVALUE', '\n']))
    try:
        # f.write('Materials...start'+ '\n')
        for wt in collector:
            try:
                paras = wt.GetOrderedParameters()
                for p in paras:
                    paraName = p.Definition.Name
                    pValue = 'no Value'
                    if(p.StorageType == StorageType.ElementId or p.StorageType == StorageType.Double or p.StorageType == StorageType.Integer):
                        if(p.AsValueString()!= None and p.AsValueString() != ''):
                            pValue = p.AsValueString()
                    elif(p.StorageType == StorageType.String):
                        if(p.AsString() != None and p.AsString() != ''):
                            pValue = p.AsString()                    
                    f.write('\t'.join([util.GetFileNameWithoutExt(revitFilePath_), str(wt.Id), util.EncodeAscii(Element.Name.GetValue(wt)), util.EncodeAscii(paraName), util.EncodeAscii(pValue), '\n']))
            except Exception as e:
                Output('Failed to get material data: ' + str(e))
                f.write('\t'.join([util.GetFileNameWithoutExt(revitFilePath_), str(wt.Id),util.EncodeAscii(Element.Name.GetValue(wt)),'\n']))
    except:
        status = False
        Output('Failed to write data file!' + fileName)
    # f.write('Materials...end')
    f.close()
    return status

# gets all materials in a model
def actionMat():  
    collector = FilteredElementCollector(doc).OfClass(Material)
    return collector

# -------------
# main:
# -------------

# build output file name
fileName_ = rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_)

Output('Writing Material Data.... start')
result_ = WriteType (actionMat, 'Materials', fileName_, doc)
Output('Writing Material Data.... status: ' + str(result_))
Output('Writing Material Data.... finished ' + fileName_)
