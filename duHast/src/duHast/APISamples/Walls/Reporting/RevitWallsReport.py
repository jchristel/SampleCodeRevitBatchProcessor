'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit walls properties report function. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.APISamples import RevitMaterials as rMat
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Walls.Utility import RevitWallsTypeSorting as rWallTypeSort
from duHast.Utilities import Utility as util

import Autodesk.Revit.DB as rdb

def get_wall_report_data(doc, revitFilePath):
    '''
    Gets wall data to be written to report file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str
    :return: list of list of sheet properties.
    :rtype: list of list of str
    '''

    data = []
    wallTypes = rWallTypeSort.GetAllWallTypes(doc)
    for wt in wallTypes:
        try:
            wallTypeName = str(rdb.Element.Name.GetValue(wt))
            cs = wt.GetCompoundStructure()
            if cs != None:
                csLayers = cs.GetLayers()
                print(len(csLayers))
                for csLayer in csLayers:
                    layerMat = rMat.GetMaterialById(doc, csLayer.MaterialId)
                    materialMark = com.get_element_mark(layerMat)
                    materialName = rMat.GetMaterialNameById(doc, csLayer.MaterialId)
                    layerFunction = str(csLayer.Function)
                    layerWidth = str(util.ConvertImperialToMetricMM(csLayer.Width)) # conversion from imperial to metric
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