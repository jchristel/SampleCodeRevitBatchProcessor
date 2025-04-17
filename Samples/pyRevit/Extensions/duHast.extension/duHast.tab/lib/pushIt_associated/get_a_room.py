

import clr
import sys
import os

from System.Collections.Generic import List


from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.utility import get_current_user_name
from duHast.Utilities.date_stamps import get_file_date_stamp, FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm


from duHast.Revit.UI.custom_selection_user import get_user_selection
from duHast.Revit.DetailItems.filled_regions import  get_filled_region_curve_loops, create_filled_region_by_view
from duHast.Revit.DetailItems.curve_create import draw_2D_lines_on_bounding_box

from duHast.Revit.Family.family_rename_loaded_families import  _rename_loaded_families
from duHast.Revit.Family.Data.Objects.family_directive_rename import FamilyDirectiveRename
from duHast.Revit.Family.family_parameter_utils import associate_parameter_with_other_parameter_on_nested_family_instance, set_parameter_formula
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.Revit.Family.family_reload import reload_all_families
from duHast.Revit.Family.family_utils import get_family_instances_of_built_in_category

from duHast.Revit.Common.Geometry.transforms import move_xyz_to_zero
from duHast.Revit.Common.Geometry.geometry import get_bounding_box_centre
from duHast.Revit.Common.Geometry.curve import create_curve_loops_through_transform
from duHast.Revit.Common.file_io import  save_as_family

from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters


from duHast.pyRevit.console_output import print_header, print_error


#from geometry import draw_2D_lines_on_bounding_box

from Autodesk.Revit.DB import BuiltInCategory, CurveLoop, Element, FilteredElementCollector, Family, ViewType, SaveAsOptions, Transform, UnitUtils, XYZ


# add path to ifc dll
SCRIPT_DIRECTORY = get_directory_path_from_file_path(__file__)
sys.path.append(os.path.join(SCRIPT_DIRECTORY , "RevitAPIIFC.dll"))
clr.AddReference("RevitAPIIFC")

# used to calculate the area of the filled region
from Autodesk.Revit.DB.IFC import ExporterIFCUtils


FAMILY_TEMPLATE_DIRECTORY = os.path.join(get_directory_path_from_file_path(__file__),"templates")


# template name for a room with walls
FAMILY_TEMPLATE_WALL_ROOM_NAME = "WLL_room_template"
FAMILY_TEMPLATE_WALL_ROOM_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_WALL_ROOM_NAME+".rft")
# template name for a bay (no walls)
FAMILY_TEMPLATE_WALL_BAY_NAME = "WLL_bay_template"
FAMILY_TEMPLATE_WALL_BAY_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_WALL_BAY_NAME+".rft")

# template name for nested generic family when in a room
FAMILY_TEMPLATE_GENERIC_ROOM_NESTED = "GEN_Inner_Nested_template"
FAMILY_TEMPLATE_GENERIC_ROOM_NESTED_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_ROOM_NESTED+".rft")
# template name for nested generic family when in a bay
FAMILY_TEMPLATE_GENERIC_BAY_NESTED = "GEN_Inner_Nested_Bay_template"
FAMILY_TEMPLATE_GENERIC_BAY_NESTED_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_BAY_NESTED+".rft")

# template name for nested generic family when in a coarse view for a room
FAMILY_TEMPLATE_GENERIC_NESTED_ROOM_COARSE = "GEN_Inner_Nested_Coarse_template"
FAMILY_TEMPLATE_GENERIC_NESTED_ROOM_COARSE_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_NESTED_ROOM_COARSE+".rft")
# template name for nested generic family when in a coarse view for a bay
FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE = "GEN_Inner_Nested_Coarse_Bay_template"
FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH = os.path.join(FAMILY_TEMPLATE_DIRECTORY, FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE+".rft")

# location to safe families to
FAMILY_OUT_DIRECTORY = r"\\proj01\SYD\016713-61A-P\2_Work\2-1_Models\2_Revit\3_Resources\1_Families\Rooms"

# overall dimension parameter names
WIDTH_PARAMETER_NAME = "HSL_WIDTH"
DEPTH_PARAMETER_NAME = "HSL_DEPTH"
HEIGHT_PARAMETER_NAME = "HSL_HEIGHT"
AREA_PARAMETER_NAME = "HSL_GROSS_FLOOR_AREA"

def get_family_from_template(doc, family_template_path):
    """
    Create a family document from a template
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_template_path: The path to the family template
    :type family_template_path: str

    :return: A result object with the family document if no exception occurred.
    :rtype: Autodesk.Revit.DB.Document
    """

    # set up a status tracker
    return_value = Result()
    
    try:
        # get the application
        app = doc.Application
        family_doc = app.NewFamilyDocument(family_template_path)
        return_value.append_message("Family document created from template: {}".format(family_template_path))
        return_value.result.append(family_doc)
    except Exception as e:
        message = "Failed to create family document from template: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def update_extrusion_outline(family_doc, curve_loop):
    # set up a status tracker
    return_value = Result()
    try:
        pass
    except Exception as e:
        message = "Failed to update extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value

def add_2D_outline(family_doc, curve_loop):
    # set up a status tracker
    return_value = Result()
    try:
        return_value.append_message("Adding 2D outline to family")
    except Exception as e:
        message = "Failed to add 2D lines in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value

def rename_nested_families(doc, family_name_mapper):
    """
    Rename nested families in the current document to match the saved family names
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_name_mapper: A dictionary of family names to rename
    :type family_name_mapper: dict
    :return: A result object with the family document if no exception occurred.
    :rtype: Autodesk.Revit.DB.Document
    """

    # set up a status tracker
    return_value = Result()
    try:

        # built rename directives
        directives = []
        for key, value in family_name_mapper.items():
            rename_directive = FamilyDirectiveRename(
                name = key, 
                category = "Generic Models", 
                file_path="", 
                new_name=value
            )
            # add the directive to the list
            directives.append(rename_directive)
        
        # rename the families in the current document
        # get all family in file
        nested_families = get_name_and_category_to_family_dict(doc)

        # rename families:
        return_value = _rename_loaded_families(
            doc=doc, 
            rename_directives = directives, 
            families=nested_families, 
            progress_callback=None,
        )

        return return_value
    except Exception as e:
        message = "Failed to rename nested families: {}".format(e)
        return_value.update_sep(False, message)
    return return_value

def hook_up_shared_parameters(doc):
    """
    Hook up shared parameters to nested families
    :param doc: The Revit family document containing nested families
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A result object.
    :rtype: Autodesk.Revit.DB.Document
    """

    # set up a status tracker
    return_value = Result()
    try:
        # get all shared parameters in the current document
        shared_paras = get_all_shared_parameters(doc)

        # get all family instances
        nested_families = get_family_instances_of_built_in_category(doc, builtin_cat=BuiltInCategory.OST_GenericModel)

        # loop over parameters and try to hook up to family instances
        for shared_para in shared_paras:
            # loop over family instances
            for fam in nested_families:

                # loop over shared parameters and attempt to hook them up to parameters on the nested instances with the same name
                associate_result = associate_parameter_with_other_parameter_on_nested_family_instance(
                    doc, 
                    nested_family_instance=fam, 
                    target_parameter_name=Element.Name.GetValue(shared_para), 
                    source_parameter_name=Element.Name.GetValue(shared_para),
                )
                return_value.update(associate_result)

        return_value.append_message("Hooked up parameters to family instances")
    except Exception as e:
        message = "Failed to hook up shared parameters in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def get_filled_region_area(filled_region):
    # set up a status tracker
    return_value = Result()
    try:
        # set the default value
        area = -1
        # get the curve loops of the filled region
        filled_region_curve_loops = get_filled_region_curve_loops(filled_region)
        # assume the second loop is the inner loop
        if len(filled_region_curve_loops) == 2:
            # get the area of the filled region
            area = ExporterIFCUtils.ComputeAreaOfCurveLoops(List[CurveLoop](filled_region_curve_loops[1]))
        else:
            area = ExporterIFCUtils.ComputeAreaOfCurveLoops(List[CurveLoop](filled_region_curve_loops[0]))
        return_value.result.append(area)
    except Exception as e:
        message = "Failed to get area: {}".format(e)
        return_value.result.append(area)
        return_value.update_sep(False, message)
    return return_value



def update_overall_dimension_parameter_values(doc, bounding_box, filled_region):
    # set up a status tracker
    return_value = Result()
    try:

        # get the overall dimension parameters
       
        # Calculate width (X dimension)
        width_bbox =  convert_imperial_feet_to_metric_mm(bounding_box.Max.X -bounding_box.Min.X)
        # Calculate depth (Y dimension)
        depth_bbox =  convert_imperial_feet_to_metric_mm(bounding_box.Max.Y -bounding_box.Min.Y)

        # get the area of the filled region depending on the number of curve loops
        area_of_interest_result =  get_filled_region_area(filled_region)
        print(area_of_interest_result)
        # check if the area of interest was found
        area_of_interest = area_of_interest_result.result[0]

        # get the family manager
        fam_manager = doc.FamilyManager
        # get all family parameters
        host_family_parameters = fam_manager.GetParameters()

        # loop over family parameters
        for host_family_parameter in host_family_parameters:

            if host_family_parameter.Definition.Name == WIDTH_PARAMETER_NAME:
                # set width
                set_parameter_formula_result = set_parameter_formula(
                    doc=doc, 
                    manager = doc.FamilyManager,
                    fam_para = host_family_parameter, 
                    formula=str(width_bbox),
                )
                return_value.update(set_parameter_formula_result)
            elif host_family_parameter.Definition.Name == DEPTH_PARAMETER_NAME:
                # set depth
                set_parameter_formula_result = set_parameter_formula(
                    doc=doc, 
                    manager = doc.FamilyManager,
                    fam_para = host_family_parameter, 
                    formula=str(depth_bbox),
                )
                return_value.update(set_parameter_formula_result)
            elif host_family_parameter.Definition.Name == HEIGHT_PARAMETER_NAME:
                # set height
                set_parameter_formula_result = set_parameter_formula(
                    doc=doc, 
                    manager = doc.FamilyManager,
                    fam_para = host_family_parameter, 
                    formula="2700", #2.7m height
                )
                return_value.update(set_parameter_formula_result)
            elif host_family_parameter.Definition.Name == AREA_PARAMETER_NAME:
                # set area
                set_parameter_formula_result = set_parameter_formula(
                    doc=doc, 
                    manager = doc.FamilyManager,
                    fam_para = host_family_parameter, 
                    formula=str(area_of_interest),
                )
                return_value.update(set_parameter_formula_result)

        return_value.append_message("Updated overall dimension parameters")
    except Exception as e:
        message = "Failed to update overall dimension parameters in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_bay_family(doc, filled_region, bounding_box):
    # set up a status tracker
    return_value = Result()

    # setup family place holders
    bay_nested_family_doc = None
    bay_nested_coarse_family_doc = None
    bay_wall_family_doc = None

    try:
        # open the bay nested family and update the extrusion outline
        fam_result = get_family_from_template(doc, family_template_path=FAMILY_TEMPLATE_GENERIC_BAY_NESTED_PATH)
        if fam_result.status == False:
            message = "Failed to create bay family: {}".format(fam_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Bay family created from template: {}".format(FAMILY_TEMPLATE_GENERIC_BAY_NESTED_PATH))
        # get the family document
        bay_nested_family_doc = fam_result.result[0]

        # update the extrusion outline
        # get the filled region curve loops
        filled_region_curve_loops = get_filled_region_curve_loops(filled_region)
        update_extrusion_result = update_extrusion_outline(bay_nested_family_doc,  filled_region_curve_loops[0])
        # check if the update extrusion was successful
        if update_extrusion_result.status == False:
            message = "Failed to update extrusion outline: {}".format(update_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay family extrusion outline updated")
        # save the family to the output directory
        nested_bay_family_name = "GEN_Inner_Nested_Bay_{}_{}".format(get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_bay_family_result = save_as_family(
            doc=bay_nested_family_doc, 
            target_directory_path=FAMILY_OUT_DIRECTORY, 
            current_full_file_name= nested_bay_family_name, 
            name_data=[[ nested_bay_family_name, nested_bay_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_bay_family_result.status == False:
            message = "Failed to save bay family: {}".format(save_nested_bay_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Nested Bay family saved to: {}".format(FAMILY_OUT_DIRECTORY))
        # close the family document
        bay_nested_family_doc.Close(False)

        # open the bay nested family coarse template
        fam_result_bay_coarse = get_family_from_template(doc, family_template_path=FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH )
        if fam_result_bay_coarse.status == False:
            message = "Failed to create nested bay coarse family: {}".format(fam_result_bay_coarse.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay coarse family created from template: \n{}".format(FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE_PATH))
        # get the family document
        bay_nested_coarse_family_doc = fam_result_bay_coarse.result[0]

        # update the extrusion outline
        update_extrusion_result = update_extrusion_outline(bay_nested_coarse_family_doc,  filled_region_curve_loops[0])
        # check if the update extrusion was successful
        if update_extrusion_result.status == False:
            message = "Failed to update extrusion outline: {}".format(update_extrusion_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay coarse family extrusion outline updated")
       
        # update add 2D lines
        add_2d_lines_result = add_2D_outline(bay_nested_coarse_family_doc,  filled_region_curve_loops[0])
        # check if the lines where added successful
        if add_2d_lines_result.status == False:
            message = "Failed to add 2D outline: {}".format(add_2d_lines_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay coarse family outline updated")

        # save the family to the output directory
        nested_bay_coarse_family_name = "GEN_Inner_Nested_Bay_Coarse_{}_{}".format(get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_nested_bay_coarse_family_result = save_as_family(
            doc=bay_nested_coarse_family_doc, 
            target_directory_path=FAMILY_OUT_DIRECTORY, 
            current_full_file_name= nested_bay_coarse_family_name, 
            name_data=[[ nested_bay_coarse_family_name, nested_bay_coarse_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_nested_bay_coarse_family_result.status == False:
            message = "Failed to save coarse bay family: {}".format(save_nested_bay_coarse_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Nested Bay coarse family saved to: {}".format(FAMILY_OUT_DIRECTORY))
        # close the family document
        bay_nested_coarse_family_doc.Close(False)

        # open the bay wall family template
        fam_wall_result = get_family_from_template(doc, family_template_path=FAMILY_TEMPLATE_WALL_BAY_PATH)
        if fam_wall_result.status == False:
            message = "Failed to create wall bay family: {}".format(fam_wall_result.message)
            return_value.update_sep(False, message)
            return return_value

        return_value.append_message("Bay wall family created from template: {}".format(FAMILY_TEMPLATE_WALL_BAY_PATH))
        # get the family document
        bay_wall_family_doc = fam_wall_result.result[0]

        # reload the nested families
        # first rename the current families with the new names
        family_name_mapper = {
            FAMILY_TEMPLATE_GENERIC_BAY_NESTED: nested_bay_family_name,
            FAMILY_TEMPLATE_GENERIC_NESTED_BAY_COARSE: nested_bay_coarse_family_name,
        }
        rename_result = rename_nested_families(doc=bay_wall_family_doc, family_name_mapper=family_name_mapper)
        # check if the rename was successful
        if rename_result.status == False:
            message = "Failed to rename nested families: {}".format(rename_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        return_value.append_message("Bay wall family: nested families renamed.")

        # reload the nested families
        reload_result = reload_all_families(
            doc=bay_wall_family_doc,
            library_location=FAMILY_OUT_DIRECTORY,
            include_sub_folders=False,
        )

        # check if the rename was successful
        if reload_result.status == False:
            message = "Failed to reload nested families: {}".format(reload_result.message)
            return_value.update_sep(False, message)
            return return_value
        return_value.append_message("Reloaded nested families successfully")

        # hook up shared parameters to nested families
        hook_up_result = hook_up_shared_parameters(doc=bay_wall_family_doc)

        # update the with and depth  parameters based on filled region bounding box dims
        # update the height parameter ( set to 2.7m default)
        update_overall_dims_result = update_overall_dimension_parameter_values(
            doc=bay_wall_family_doc, bounding_box=bounding_box, filled_region=filled_region)
        
        # check if the update was successful
        if update_overall_dims_result.status == False:
            message = "Failed to update overall dimension parameters: {}".format(update_overall_dims_result.message)
            return_value.update_sep(False, message)
            return return_value
        
        # save the wall family to the output directory first
        wall_bay_family_name = "WLL_Bay_{}_{}".format(get_current_user_name(), get_file_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC))
        save_wall_bay_family_result = save_as_family(
            doc=bay_wall_family_doc, 
            target_directory_path=FAMILY_OUT_DIRECTORY, 
            current_full_file_name= wall_bay_family_name, 
            name_data=[[ wall_bay_family_name,wall_bay_family_name]], 
            file_extension=".rfa",
            compact_file = True,
        )
        # check if the save was successful
        if save_wall_bay_family_result.status == False:
            message = "Failed to save wall bay family: {}".format(save_wall_bay_family_result.message)
            return_value.update_sep(False, message)
            return return_value

        # close the wall family document
        bay_wall_family_doc.Close(False)

        # add the family path to the result object and return it
        return_value.append_message("Bay wall family saved to: {}".format(FAMILY_OUT_DIRECTORY))
        return_value.result.append("{}{}.rfa".format(FAMILY_OUT_DIRECTORY, wall_bay_family_name))

    except Exception as e:
        message = "Failed to create bay family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_room_family(doc, filled_region):
    return_value = Result()
    try:
        pass
    except Exception as e:
        message = "Failed to create bay family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value



def create_family_from_filled_region(doc, filled_region, bounding_box):

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
        bay_result = create_bay_family(doc=doc, filled_region=filled_region, bounding_box=bounding_box)
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

    # get the selection filter for grids
    selection_filter_grids = selection_filter_filled_regions
    # get user to select grids
    grids_selected_result = get_user_selection(
        doc=doc,
        uidoc=uiapp.ActiveUIDocument,
        ui_text="Select filled regions",
        selection_filter=selection_filter_grids,
    )

    # check if mock rooms where selected
    if grids_selected_result.status == False:
        return_value.update(grids_selected_result)
        print("Failed to select filled regions: {}".format(grids_selected_result.message))
        return return_value

    # get the actual push it mock rooms selected
    filled_regions_selected = grids_selected_result.result[0]
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

        create_family_result = create_family_from_filled_region(doc, f, bounding_box=bounding_box_new)
        if( create_family_result.status == False):
            message = "Failed to create family from filled region: \n{}".format(create_family_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            continue
        else:
            print("Created family: {}".format(create_family_result.message))
