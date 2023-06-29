"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for material reports. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Utilities import files_io as fileIO, utility as util
from duHast.Revit.Materials.materials import get_all_materials


def get_material_report_data(doc, revit_file_path):
    """
    Gets material data ready for being written to file.
    - HOSTFILE
    - ID
    - NAME
    - and any parameter names and values attached to a material
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The fully qualified file path of Revit file.
    :type revit_file_path: str
    :return: The material data in a nested list of string
    :rtype: list of list of str
    """

    data = []
    mats = get_all_materials(doc)
    for mat in mats:
        try:
            paras = mat.GetOrderedParameters()
            for p in paras:
                para_name = p.Definition.Name
                p_value = rParaGet.get_parameter_value(p)
                data.append(
                    [
                        revit_file_path,
                        str(mat.Id),
                        util.encode_ascii(rdb.Element.Name.GetValue(mat)),
                        util.encode_ascii(para_name),
                        util.encode_ascii(p_value),
                    ]
                )
        except Exception:
            data.append(
                [
                    fileIO.get_file_name_without_ext(revit_file_path),
                    str(mat.Id),
                    util.encode_ascii(rdb.Element.Name.GetValue(mat)),
                ]
            )
    return data
