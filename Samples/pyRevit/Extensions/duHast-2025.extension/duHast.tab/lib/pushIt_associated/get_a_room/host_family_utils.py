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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from duHast.Revit.Family.Data.Objects.family_directive_rename import FamilyDirectiveRename
from duHast.Revit.Family.family_instance_create import place_a_family_instance_by_level
from duHast.Revit.Family.family_rename_loaded_families import  _rename_loaded_families
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.Revit.Family.family_parameter_utils import associate_parameter_with_other_parameter_on_nested_family_instance, set_parameter_formula
from duHast.Revit.Family.family_utils import get_family_instances_of_built_in_category, load_family

from duHast.Revit.Common.parameter_set_utils import set_builtin_parameter_without_transaction_wrapper_by_name

from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters

from pushIt_associated.get_a_room import settings

from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Element

def rename_nested_families(doc, family_name_mapper):
    """
    Rename nested families in the current document to match the saved family names
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_name_mapper: A dictionary of family names to rename
    :type family_name_mapper: dict
    
    :return: Result class instance.

        - `result.status` (bool): True if the nested families where renamed successfully, otherwise False.
        - `result.message` (str): Confirmation of successful rename.
        - `result.result` (list): Empty.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
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
    
    :return: Result class instance.

        - `result.status` (bool): True if the shared parameters where hooked up successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): Empty
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
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


def update_overall_dimension_parameter_values(family_doc, family_config):
    """
    Update overall dimension parameter values in the family document.
    This includes width, depth, height, and area parameters.
    
    :param doc: The Revit family document
    :type doc: Autodesk.Revit.DB.Document
    :param family_config: The family configuration object containing bounding box and area information
    :type family_config: FamilyTypeConfig
    
    :return: Result class instance.

        - `result.status` (bool): True if the overall dimension parameters where updated successfully, otherwise False.
        - `result.message` (str): Confirmation of successful update.
        - `result.result` (list): Empty.

    On exception:

        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """
    
    # set up a status tracker
    return_value = Result()
    try:

        # get the overall dimension parameters
       
        # Calculate width (X dimension)
        width_bbox =  convert_imperial_feet_to_metric_mm(family_config.bounding_box.Max.X - family_config.bounding_box.Min.X)
        # Calculate depth (Y dimension)
        depth_bbox =  convert_imperial_feet_to_metric_mm(family_config.bounding_box.Max.Y - family_config.bounding_box.Min.Y)

        # get the area of the filled region
        area_of_interest = family_config.area

        # get the family manager
        fam_manager = family_doc.FamilyManager
        # get all family parameters
        host_family_parameters = fam_manager.GetParameters()

        # loop over family parameters
        for host_family_parameter in host_family_parameters:

            if host_family_parameter.Definition.Name == settings.WIDTH_PARAMETER_NAME:
                # set width
                set_parameter_formula_result = set_parameter_formula(
                    doc=family_doc, 
                    manager =fam_manager,
                    fam_para = host_family_parameter, 
                    formula=str(width_bbox),
                )
                return_value.update(set_parameter_formula_result)
            elif host_family_parameter.Definition.Name == settings.DEPTH_PARAMETER_NAME:
                # set depth
                set_parameter_formula_result = set_parameter_formula(
                    doc=family_doc, 
                    manager = fam_manager,
                    fam_para = host_family_parameter, 
                    formula=str(depth_bbox),
                )
                return_value.update(set_parameter_formula_result)
            elif host_family_parameter.Definition.Name == settings.HEIGHT_PARAMETER_NAME:
                # set height
                set_parameter_formula_result = set_parameter_formula(
                    doc=family_doc, 
                    manager = fam_manager,
                    fam_para = host_family_parameter, 
                    formula="2700", #2.7m height
                )
                return_value.update(set_parameter_formula_result)
            elif host_family_parameter.Definition.Name == settings.AREA_DESIGNED_PARAMETER_NAME:
                # set area
                set_parameter_formula_result = set_parameter_formula(
                    doc=family_doc, 
                    manager = fam_manager,
                    fam_para = host_family_parameter, 
                    formula=str(area_of_interest),
                )
                return_value.update(set_parameter_formula_result)

        return_value.append_message("Updated overall dimension parameters")
    except Exception as e:
        message = "Failed to update overall dimension parameters in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def load_push_it_family(doc, file_path):
    """
    Load the PushIt family into the Revit document.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param file_path: The file path of the PushIt family
    :type file_path: str
    
    :return: Result class instance.

        - `result.status` (bool): True if the family was loaded successfully, otherwise False.
        - `result.message` (str): Confirmation of successful load.
        - `result.result` (list): Empty.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()
    try:
        # load the family
        load_family_result = load_family(
            doc=doc, 
            family_file_path=file_path, 
        )
       
        return_value.update(load_family_result)

    except Exception as e:
        message = "Failed to load PushIt family with error: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_push_it_family_instance (doc, push_it_family, location_point, active_view):
    """
    Create a PushIt family instance in the Revit document.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param push_it_family: The PushIt family to create an instance of
    :type push_it_family: Autodesk.Revit.DB.FamilySymbol
    :param filled_region: The filled region to place the PushIt family instance in
    :type filled_region: Autodesk.Revit.DB.FilledRegion
    :param active_view: The view of which the associated level is to be used to place the instance on.
    :type active_view: Autodesk.Revit.DB.View
    
    :return: Result class instance.

        - `result.status` (bool): True if the family instance was created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): Empty.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()
    try:
        # get the level of the active view
        level = active_view.GenLevel
       
        # get the family symbol
        family_symbol_ids = push_it_family.GetFamilySymbolIds()

        family_symbol = None

        for symbol_is in family_symbol_ids:
            family_symbol = doc.GetElement(symbol_is)
            break

        # set up an action ensuring offset from the host ( level ) is set to 0
        def action(element):
            action_return_value = Result()
            try:
                set_offset_result = set_builtin_parameter_without_transaction_wrapper_by_name(
                    element=element,
                    parameter_definition=BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM,
                    parameter_value=0.0,
                )
                action_return_value.update(set_offset_result)
            except Exception as e:
                message = "Failed to set offset parameter with error: {}".format(e)
                action_return_value.update_sep(False, message)
            return action_return_value

        # place an instance of the family symbol
        place_result = place_a_family_instance_by_level(
            doc,
            location_point,
            family_symbol=family_symbol,
            target_placement_level= level,
            modify_action=action,
        )

        return_value.update(place_result)
       
    except Exception as e:
        message = "Failed to place PushIt family with error: {}".format(e)
        return_value.update_sep(False, message)
    return return_value
