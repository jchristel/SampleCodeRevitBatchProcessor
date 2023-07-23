"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the hRevit shared parameter report functionality.
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
from duHast.Revit.SharedParameters.shared_parameters import (
    get_all_shared_parameters,
    param_binding_exists,
    param_binding_exists_2023,
)
from duHast.Utilities.utility import encode_ascii
from duHast.Revit.Common import revit_version as rRev


def get_shared_parameter_report_data(doc, revit_file_path):
    """
    Gets shared parameter data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The file hostname, which is added to data returned.
    :type revit_file_path: str
    :return: list of list of parameter properties.
    :rtype: list of list of str
    """

    data = []
    paras = get_all_shared_parameters(doc)

    # get revit version
    revit_version = rRev.get_revit_version_number(doc)
    for p in paras:
        if revit_version <= 2022:
            parameter_definition = p.GetDefinition()
            parameter_bindings = []
            # parameter bindings do not exist in a family document
            if doc.IsFamilyDocument == False:
                parameter_bindings = param_binding_exists(
                    doc,
                    rdb.Element.Name.GetValue(p),
                    parameter_definition.ParameterType,
                )
            # just in case parameter name is not unicode
            parameter_name = "unknown"
            try:
                parameter_name = encode_ascii(rdb.Element.Name.GetValue(p))
            except Exception as ex:
                parameter_name = "Exception: {}".format(ex)
            # build data
            data.append(
                [
                    revit_file_path,
                    p.GuidValue.ToString(),
                    str(p.Id.IntegerValue),
                    parameter_name,
                    str(parameter_bindings),
                ]
            )
        else:
            parameter_definition = p.GetDefinition()
            parameter_bindings = []
            data_type_id = parameter_definition.GetDataType()  # forge type id
            # parameter bindings do not exist in a family document
            if doc.IsFamilyDocument == False:
                # uses forge type id
                parameter_bindings = param_binding_exists(
                    doc, rdb.Element.Name.GetValue(p), data_type_id
                )
            # just in case parameter name is not unicode
            parameter_name = "unknown"
            try:
                parameter_name = encode_ascii(rdb.Element.Name.GetValue(p))
            except Exception as ex:
                parameter_name = "Exception: {}".format(ex)
            # build data
            data.append(
                [
                    revit_file_path,
                    p.GuidValue.ToString(),
                    str(p.Id.IntegerValue),
                    parameter_name,
                    str(parameter_bindings),
                ]
            )
    return data
