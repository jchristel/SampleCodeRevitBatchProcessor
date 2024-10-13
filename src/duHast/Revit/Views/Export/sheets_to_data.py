"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit sheet to data sheet conversion. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Revit.Views.views import get_viewport_on_sheets
from duHast.Revit.Views.Export.view_ports_to_data import convert_revit_viewport_to_data_instance
from duHast.Data.Objects.data_sheet import DataSheet
from duHast.Revit.Exports.export_data import get_instance_properties

def convert_revit_sheet(doc, sheet):
    """
    Convertes a revit sheet to a data instance sheet.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: A revit sheet
    :type sheet: Autodesk.Revit.DB.view

    :return: A data sheet instance
    :rtype: :class:`.DataSheet`
    """

    # instantiate new data sheet object
    data_sheet = DataSheet()

    # get instance properties
    data_sheet.instance_properties.id = sheet.Id.IntegerValue
    
    # get any instance parameters properties
    instance_properties = get_instance_properties(sheet) 
    data_sheet.instance_properties = instance_properties
    
    # get view ports on sheet
    revit_view_ports = get_viewport_on_sheets(doc=doc,sheets= [sheet])

    # convert to data objects
    view_ports_converted = []
    for revit_view_port in revit_view_ports:
        view_port_data = convert_revit_viewport_to_data_instance(doc=doc, revit_view_port=revit_view_port)
        
        # check if this is a view port of interest, otherwise ignore
        if view_port_data:
            view_ports_converted.append(view_port_data)
    
    # add them to sheet
    data_sheet.view_ports = view_ports_converted
    return data_sheet