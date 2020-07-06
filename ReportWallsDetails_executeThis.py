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
debugRevitFileName_ = r'C:\temp\Test_walls.rvt'

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    from revit_script_util import Output
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
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

#
def WriteType (action, description, fileName, doc):
    status = True
    collector = action()
    print ('Writing ' + description +'....')
    f = open(fileName, 'w')
    f.write('\t'.join(['HOSTFILE', 'WALLTYPEID', 'WALLTYPENAME', 'FUNCTION', 'LAYERWIDTH', 'LAYERMATERIALNAME', '\n']))
    try:
        #f.write('Wall Types...start'+ '\n')
        for wt in collector:
            try:
                cs = wt.GetCompoundStructure()
                if cs != None:
                    csls = cs.GetLayers()
                    for csl in csls:
                        materialName = str(GetMaterialbyId (csl.MaterialId, doc))
                        wallTypeName = str(Element.Name.GetValue(wt))
                        function = str(csl.Function)
                        width = str(csl.Width*304.8)
                        f.write('\t'.join([GetRevitFileName(revitFilePath_), str(wt.Id), EncodeAscii(wallTypeName), function, width, EncodeAscii(materialName), '\n']))
                else:                 
                    f.write('\t'.join([GetRevitFileName(revitFilePath_), str(wt.Id), EncodeAscii(Element.Name.GetValue(wt)), '\n']))
            except Exception as inst:
                f.write('\t'.join([GetRevitFileName(revitFilePath_) , str(wt.Id), Element.Name.GetValue(wt), '\n']))
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
    #f.write('Wall Types...end')
    f.close()
    return status

#returns a materials mark and name based on a material id
def GetMaterialbyId (id, doc):
    collector = FilteredElementCollector(doc)
    collector.OfClass(Material)
    for m in collector:
        if m.Id.IntegerValue == id.IntegerValue:
            return GetNameAndMark(m)

#returns the material mark and defintion name in format:
#{mark}{name}
def GetNameAndMark (mat):
    paraName = Element.Name.GetValue(mat)
    name= '{}' if paraName == None else '{' + paraName + '}'
    paraMark = mat.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
    mark= '{}' if paraMark == None else '{' + paraMark.AsString() + '}'
    return name + mark

#gets all wall types in a model
#this includes types of curtain walls as well as any in types of place wall families!
def actionWT():  
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType()
    return collector

# -------------
# main:
# -------------

#build output file name
fileName_ = rootPath_ + '\\'+ GetOutPutFileName(revitFilePath_)

Output('Writing Wall Type Data.... start')
#write out wall type data
result_ = WriteType (actionWT, 'wall type', fileName_, doc)
Output('Writing Wall Type Data.... status: ' + str(result_))
Output('Writing Wall Type Data.... finished ' + fileName_)
