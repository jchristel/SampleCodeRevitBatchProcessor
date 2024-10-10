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
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from duHast.Revit.Materials.materials import get_material_name_by_id
from duHast.Revit.Common.common import get_element_mark
from duHast.Revit.Walls.walls import get_all_wall_types_by_category
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm
from duHast.Utilities.utility import encode_ascii

from Autodesk.Revit.DB import Element


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
            wall_type_name = str(Element.Name.GetValue(wt))
            cs = wt.GetCompoundStructure()
            if cs != None:
                cs_layers = cs.GetLayers()
                # print(len(cs_layers))
                for cs_layer in cs_layers:
                    layer_mat = doc.GetElement(cs_layer.MaterialId)
                    material_mark = material_name = "N/A"
                    # not all layers may have assigned a material (could be Default)
                    if layer_mat is not None:
                        material_mark = get_element_mark(layer_mat)
                        material_name = get_material_name_by_id(
                            doc, cs_layer.MaterialId
                        )
                    layer_function = str(cs_layer.Function)
                    layer_width = str(
                        convert_imperial_feet_to_metric_mm(cs_layer.Width)
                    )  # conversion from imperial to metric
                    data.append(
                        [
                            revit_file_path,
                            str(wt.Id),
                            encode_ascii(wall_type_name),
                            layer_function,
                            layer_width,
                            encode_ascii(material_name),
                            encode_ascii(material_mark),
                        ]
                    )
            else:
                data.append(
                    [
                        revit_file_path,
                        str(wt.Id),
                        encode_ascii(wall_type_name),
                        "no layers - in place family or curtain wall",
                        str(0.0),
                        "NA",
                        "NA",
                    ]
                )
        except:
            data.append([revit_file_path, str(wt.Id)])
    return data
