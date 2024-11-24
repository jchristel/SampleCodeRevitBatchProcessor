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

from duHast.Revit.Exports.export_data import get_instance_properties
from duHast.Revit.Views.views import get_viewport_on_sheets
from duHast.Revit.Views.Export.view_ports_to_data import (
    convert_revit_viewport_to_data_instance,
    convert_revit_schedule_sheet_instances_to_data_instance,
)
from duHast.Data.Objects.Collectors.data_sheet import DataSheet
from duHast.Revit.Views.sheets import get_sheets_by_filters, get_title_block_from_sheet
from duHast.Revit.Views.schedules import get_schedule_instance_on_sheet
from duHast.Revit.Common.Geometry.to_data_conversion import convert_revit_bounding_box_to_geometry2_bounding_box
from duHast.Data.Objects.Collectors.Properties.data_sheet_size_names import DataSheetSizeNames


def get_title_block_size(doc, sheet):
    
    title_block_instance = get_title_block_from_sheet(doc=doc, sheet=sheet)
    if title_block_instance is None:
        return None
    
    # get a 2D bounding box from the title block instance
    bbox = convert_revit_bounding_box_to_geometry2_bounding_box(bounding_box=title_block_instance.BoundingBox())
    
    # get supported sheet sizes
    sheet_sizes_names= DataSheetSizeNames()
    sizes = sheet_sizes_names.get_all_supported_sizes()
    
    # find a match
    for supported_size in sizes:
        if(supported_size.is_matching_size(width=bbox.width, height=bbox.depth)):
            return supported_size.name
    
    # uh no match found...
    return None
    
    
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
    
    # get the sheet size
    

    # get any instance parameters properties
    instance_properties = get_instance_properties(sheet)
    data_sheet.instance_properties = instance_properties

    # get view ports on sheet
    revit_view_ports = get_viewport_on_sheets(doc=doc, sheets=[sheet])

    # convert to data objects
    view_ports_converted = []
    for revit_view_port in revit_view_ports:
        view_port_data = convert_revit_viewport_to_data_instance(
            doc=doc, revit_view_port=revit_view_port
        )

        # check if this is a view port of interest, otherwise ignore
        if view_port_data:
            view_ports_converted.append(view_port_data)

    # get schedule instances on sheet
    schedule_sheet_instances = get_schedule_instance_on_sheet(doc, sheet)
    if schedule_sheet_instances and len(schedule_sheet_instances) > 0:
        instances_converted = convert_revit_schedule_sheet_instances_to_data_instance(
            doc=doc,
            sheet=sheet,
            revit_schedule_sheet_instances=schedule_sheet_instances,
        )
        view_ports_converted = view_ports_converted + instances_converted

    # add them to sheet
    data_sheet.view_ports = view_ports_converted
    return data_sheet


def get_all_sheet_data(doc):
    """
    Gets a list of sheet data objects for each sheet element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data sheet instances.
    :rtype: list of :class:`.DataSheet`
    """

    all_sheet_data = []
    sheets = get_sheets_by_filters(doc=doc, view_rules=None)
    for sheet in sheets:
        sd = convert_revit_sheet(doc=doc, sheet=sheet)
        if sd is not None:
            all_sheet_data.append(sd)
    return all_sheet_data
