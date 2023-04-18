'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for material reports. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Utility as util, FilesIO as util
from duHast.APISamples.Materials.RevitMaterials import get_all_materials

def get_material_report_data(doc, revitFilePath):
    '''
    Gets material data ready for being written to file.
    - HOSTFILE
    - ID
    - NAME
    - and any parameter names and values attached to a material
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path of Revit file.
    :type revitFilePath: str
    :return: The material data in a nested list of string
    :rtype: list of list of str
    '''

    data = []
    mats = get_all_materials(doc)
    for mat in mats:
        try:
            paras = mat.GetOrderedParameters()
            for p in paras:
                paraName = p.Definition.Name
                pValue = rParaGet.get_parameter_value(p)
                data.append(
                    [revitFilePath,
                    str(mat.Id),
                    util.EncodeAscii(rdb.Element.Name.GetValue(mat)),
                    util.EncodeAscii(paraName),
                    util.EncodeAscii(pValue)]
                )
        except Exception:
            data.append([
                util.get_file_name_without_ext(revitFilePath),
                str(mat.Id),
                util.EncodeAscii(rdb.Element.Name.GetValue(mat))
            ])
    return data