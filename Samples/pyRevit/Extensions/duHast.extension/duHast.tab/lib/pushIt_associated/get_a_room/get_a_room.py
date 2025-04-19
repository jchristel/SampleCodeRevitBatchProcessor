# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from System.Collections.Generic import List


from duHast.Utilities.Objects.result import Result

from duHast.Revit.UI.custom_selection_user import get_user_selection
from duHast.Revit.DetailItems.filled_regions import  get_filled_region_curve_loops
from duHast.Revit.DetailItems.filled_regions_create import create_filled_region_by_view
from duHast.Revit.DetailItems.curve_create import draw_2D_lines_on_bounding_box

from duHast.Revit.Common.Geometry.transforms import move_xyz_to_zero
from duHast.Revit.Common.Geometry.geometry import get_bounding_box_centre
from duHast.Revit.Common.Geometry.curve_loops import create_curve_loops_through_transform

from duHast.Revit.ExtensibleSchemas.extensible_schemas import does_schema_exist

from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.directory_picker import get_process_directory

from pushIt_associated.get_a_room import settings
from pushIt_associated.get_a_room.nested_family_bay_create import create_bay_family
from pushIt_associated.get_a_room.nested_family_room_create import create_room_family
from pushIt_associated.get_a_room.settings_utils import get_output_path_from_schema


from Autodesk.Revit.DB import Element, ViewType



def create_family_from_filled_region(doc, filled_region, bounding_box, output_directory):

    """
    Create a family from a filled region
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param filled_region: The filled region to create the family from
    :type filled_region: Autodesk.Revit.DB.FilledRegion

    :return: A result object with the family document if no exception occurred.
    :rtype: Autodesk.Revit.DB.Document
    """

    # set up a status tracker
    return_value = Result()

    # check how many curves are in the filled region
    filled_region_curve_loops = get_filled_region_curve_loops(filled_region)

    # check which family to create
    if len (filled_region_curve_loops) == 1:
        # create a bay family
        bay_result = create_bay_family(doc=doc, filled_region=filled_region, bounding_box=bounding_box, output_directory=output_directory)
        return_value.update(bay_result)
    elif len (filled_region_curve_loops) == 2:
        # create a room family
        room_result = create_room_family(doc=doc, filled_region=filled_region)
        return_value.update(room_result)

    else:
        message = "Filled region has more than 2 curves"
        return_value.update_sep(False, message)
    return return_value


def selection_filter_filled_regions(elem):
    """
    Returns True if the element is of category grids

    :param elem: A revit element
    :type elem: Autodesk.Revit.DB.Element
    :return: True if the element is of category grids, otherwise False
    :rtype: bool
    """

    if Element.Name.GetValue(elem)  == "Detail Filled Region":
        return True
    else:
        return False
    
    
def get_a_room_entry(doc, uiapp,output, forms):
    """
    Test function to select filled regions in Revit
    """
    # set up a status tracker
    return_value = Result()

    print_header("Get A Room Entry")
    
    # check ig extensible schema exists
    if not does_schema_exist(settings.GET_A_ROOM_ADD_IN_GUID):
        message = "Extensible schema does not exist. Please run the setup add-in first."
        return_value.update_sep(False, message)
        print_error(message)
        return return_value
    
    # get the output directory from the schema
    output_directory = get_output_path_from_schema()
    if output_directory is None or output_directory == "":
        # get the user to select one ...for now
        selection_result = get_process_directory(forms=forms, form_title="Select output directory")
        if selection_result.status == False:
            message = "Failed to select output directory: {}".format(selection_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        else:
            output_directory = selection_result.result[0]
        
    # get the selection filter for grids
    selection_filter_filled_regions = selection_filter_filled_regions
    # get user to select grids
    filled_regions_selected_result = get_user_selection(
        doc=doc,
        uidoc=uiapp.ActiveUIDocument,
        ui_text="Select filled regions",
        selection_filter=selection_filter_filled_regions,
    )

    # check if mock rooms where selected
    if filled_regions_selected_result.status == False:
        return_value.update(filled_regions_selected_result)
        print_error("Failed to select filled regions: {}".format(filled_regions_selected_result.message))
        return return_value

    # get the actual push it mock rooms selected
    filled_regions_selected = filled_regions_selected_result.result[0]
    if len(filled_regions_selected) == 0:
        message = "No filled regions where selected."
        return_value.update_sep(False, message)
        print(message)
        return return_value
    
    # set up a progress counter
    counter = 1

    filtered_regions = []

    for f in filled_regions_selected:
        # get the filled region curve loops
        filled_region_curve_loops = get_filled_region_curve_loops(f)
        # check if the filled region has curves
        if filled_region_curve_loops is None:
            message = "No curves found in filled region."
            return_value.update_sep(False, message)
            print(message)
            return return_value

        # print the filled region curve loops
        print("Filled region {} has {} curves".format(f.Name, len(filled_region_curve_loops)))
        
        # reject any filled region with a curve loop count greater than 2
        if len(filled_region_curve_loops) > 2:
            message = "Filled region {} has more than 2 curves".format(f.Name)
            return_value.update_sep(False, message)
            print(message)
        else:
            # add the filled region to the filtered regions
            filtered_regions.append(f)
            print("Filled region {} is valid".format(f.Name))
            

    # get the active view
    active_view = doc.ActiveView

    # check if the active view is a floor plan
    if active_view.ViewType != ViewType.FloorPlan:
        message = "Active view is not a floor plan."
        return_value.update_sep(False, message)
        print(message)
        return return_value
    
    # loop over the filtered regions
    for f in filtered_regions:
        # get the bounding box of the filled region
        bounding_box = f.get_BoundingBox(active_view)
        result_draw = draw_2D_lines_on_bounding_box(doc, bounding_box, active_view)

        # attempt to move the bounding box to centre to zero
        # get the bounding box center
        bounding_box_center = get_bounding_box_centre(bounding_box)
        # get the transform to move the bounding box to zero
        transform_to_origin = move_xyz_to_zero(bounding_box_center)

        # create a copy of the original curve loop via transform
        transformed_curve_loops = create_curve_loops_through_transform(
            curve_loops=get_filled_region_curve_loops(f), 
            transform=transform_to_origin,
            convert_net_list=True
        )
        
        # create a new filled region by view
        filled_region_new_result = create_filled_region_by_view(
            doc=doc, 
            view=active_view, 
            curve_loops=transformed_curve_loops,
            filled_region_type=f.GetTypeId(),
        )

        if filled_region_new_result.status == False:
            message = "Failed to create new filled region: {}".format(filled_region_new_result.message)
            return_value.update_sep(False, message)
            print(message)
            continue
        bounding_box_new = filled_region_new_result.result[0].get_BoundingBox(active_view)
        # draw the transformed bounding box
        result_draw = draw_2D_lines_on_bounding_box(doc, bounding_box_new , active_view)

        create_family_result = create_family_from_filled_region(doc, f, bounding_box=bounding_box_new, output_directory=output_directory)
        if( create_family_result.status == False):
            message = "Failed to create family from filled region: \n{}".format(create_family_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            continue
        else:
            print("Created family: {}".format(create_family_result.message))
    
    
    print("Finished.")
