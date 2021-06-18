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
import RevitMaterials as rMat
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_WALLS_HEADER = ['HOSTFILE', 'WALLTYPEID', 'WALLTYPENAME', 'FUNCTION', 'LAYERWIDTH', 'LAYERMATERIALNAME', 'LAYERMATERIALMARK']

# --------------------------------------------- utility functions ------------------

# returns all wall types in a model
# doc:   current model document
def GetAllWallTypes(doc):  
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType()
    return collector

# ------------------------------------------------------- walls reporting --------------------------------------------------------------------

# gets wall data ready for being printed to file
# doc: the current revit document
# revitFilePath: fully qualified file path of Revit file
def GetWallReportData(doc, revitFilePath):
    data = []
    wallTypes = GetAllWallTypes(doc)
    for wt in wallTypes:
        try:
            wallTypeName = str(Element.Name.GetValue(wt))
            cs = wt.GetCompoundStructure()
            if cs != None:
                csls = cs.GetLayers()
                print(len(csls))
                for csl in csls:
                    layerMat = rMat.GetMaterialbyId(doc, csl.MaterialId)
                    materialMark = com.GetElementMark(layerMat)
                    materialName = rMat.GetMaterialNameById(doc, csl.MaterialId)
                    layerFunction = str(csl.Function)
                    layerWidth = str(util.ConvertImperialToMetricMM(csl.Width)) # conversion from imperial to metric
                    data.append([
                        revitFilePath, 
                        str(wt.Id), 
                        util.EncodeAscii(wallTypeName),
                        layerFunction, 
                        layerWidth, 
                        util.EncodeAscii(materialName),
                        util.EncodeAscii(materialMark)
                        ])
            else:
                data.append([
                    revitFilePath, 
                    str(wt.Id), 
                    util.EncodeAscii(wallTypeName),
                    'no layers - in place family or curtain wall',
                    str(0.0),
                    'NA',
                    'NA'
                ])              
        except:
            data.append([
                revitFilePath, 
                str(wt.Id)
            ])
    return data