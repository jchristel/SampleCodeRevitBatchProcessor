'''
This module contains a number of helper functions relating to Revit materials. 
'''
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
from Autodesk.Revit.DB import FilteredElementCollector, Material, Element

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_MATERIALS_HEADER = ['HOSTFILE', 'ID', 'MATERIALNAME', 'PARAMETERNAME', 'PARAMETERVALUE']

# --------------------------------------------- utility functions ------------------

# returns all materials in a model
# doc:   current model document
def GetAllMaterials(doc):  
    collector = FilteredElementCollector(doc).OfClass(Material)
    return collector

# returns a material element based on a material id
# doc:  current model document
# id:   id of material to be returned
def GetMaterialbyId(doc, id):
    mats = GetAllMaterials(doc)
    for m in mats:
        if m.Id.IntegerValue == id.IntegerValue:
            return m

# returns a material name based on a material id
# doc:  current model document
# id:   id of material name to be returned
def GetMaterialNameById(doc, id):
    name = '<By Category>'
    mats = GetAllMaterials(doc)
    for m in mats:
        if m.Id.IntegerValue == id.IntegerValue:
            mName = Element.Name.GetValue(m)
            name = '' if mName == None else mName
    return name
# ------------------------------------------------------- Material reporting --------------------------------------------------------------------

# gets material ready for being printed to file
# doc: the current revit document
# revitFilePath: fully qualified file path of Revit file
def GetMaterialReportData(doc, revitFilePath):
    data = []
    mats = GetAllMaterials(doc)
    for mat in mats:
        try:
            paras = mat.GetOrderedParameters()
            for p in paras:
                paraName = p.Definition.Name
                pValue = com.getParameterValue(p)
                data.append(
                    [revitFilePath,
                    str(mat.Id),
                    util.EncodeAscii(Element.Name.GetValue(mat)),
                    util.EncodeAscii(paraName),
                    util.EncodeAscii(pValue)]
                )                  
        except Exception:
            data.append([
                util.GetFileNameWithoutExt(revitFilePath), 
                str(mat.Id),
                util.EncodeAscii(Element.Name.GetValue(mat))
            ])
    return data