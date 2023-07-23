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
# BSD License
# Copyright © 2023, Jan Christel
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
