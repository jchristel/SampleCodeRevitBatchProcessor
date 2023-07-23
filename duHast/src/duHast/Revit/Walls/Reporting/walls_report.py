"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit walls properties report function. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Revit.Materials import materials as rMat
from duHast.Revit.Common import common as com
from duHast.Revit.Walls.Utility import walls_type_sorting as rWallTypeSort
from duHast.Revit.Walls.walls import get_all_wall_types_by_category
from duHast.Utilities import utility as util
import duHast.Utilities.unit_conversion

import Autodesk.Revit.DB as rdb


def get_wall_report_data(doc, revit_file_path):
    """
    Gets wall data to be written to report file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The file hostname, which is added to data returned.
    :type revit_file_path: str
    :return: list of list of sheet properties.
    :rtype: list of list of str
    """

    data = []
    wall_types = get_all_wall_types_by_category(doc)
    for wt in wall_types:
        try:
            wall_type_name = str(rdb.Element.Name.GetValue(wt))
            cs = wt.GetCompoundStructure()
            if cs != None:
                cs_layers = cs.GetLayers()
                # print(len(cs_layers))
                for cs_layer in cs_layers:
                    layer_mat = doc.GetElement(cs_layer.MaterialId)
                    material_mark = material_name = "N/A"
                    # not all layers may have assigned a material (could be Default)
                    if layer_mat is not None:
                        material_mark = com.get_element_mark(layer_mat)
                        material_name = rMat.get_material_name_by_id(
                            doc, cs_layer.MaterialId
                        )
                    layer_function = str(cs_layer.Function)
                    layer_width = str(
                        duHast.Utilities.unit_conversion.convert_imperial_feet_to_metric_mm(
                            cs_layer.Width
                        )
                    )  # conversion from imperial to metric
                    data.append(
                        [
                            revit_file_path,
                            str(wt.Id),
                            util.encode_ascii(wall_type_name),
                            layer_function,
                            layer_width,
                            util.encode_ascii(material_name),
                            util.encode_ascii(material_mark),
                        ]
                    )
            else:
                data.append(
                    [
                        revit_file_path,
                        str(wt.Id),
                        util.encode_ascii(wall_type_name),
                        "no layers - in place family or curtain wall",
                        str(0.0),
                        "NA",
                        "NA",
                    ]
                )
        except:
            data.append([revit_file_path, str(wt.Id)])
    return data
