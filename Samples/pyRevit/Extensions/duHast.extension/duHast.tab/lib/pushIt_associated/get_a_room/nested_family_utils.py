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

from duHast.Revit.Family.family_element_utils import get_all_curve_based_elements_in_family,get_all_generic_forms_in_family, set_element_visibility_by_detail_level
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Revit.Family.Geometry.extrusion_create import create_extrusion_on_level, associate_extrusion_height_with_parameter, set_extrusion_sub_category
from duHast.Revit.Family.Geometry.symbolic_curve_create import create_symbolic_curves_on_level, set_symbolic_curve_sub_category

from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_category_graphic_style_ids,
)

from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Categories.categories import (
    ELEMENTS_PARAS_SUB,
    get_category_by_id,
)

#from Autodesk.Revit.DB import BuiltInParameter, CurveArrArray, CurveArray, CurveLoop, Curve, Extrusion, ModelLine ,Transaction, SketchPlane


def get_family_element_sub_category_id_name(doc, extrusion):
    """
    Get the sub category, sub category id and subcategory name of elements in a family document.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param extrusion: The extrusion element.
    :type extrusion: Autodesk.Revit.DB.Extrusion
    :return: A tuple with the sub category, sub category id and subcategory name.
    :rtype: tuple (Autodesk.Revit.DB.Category, Autodesk.Revit.DB.ElementId, str)
    """

    extrusion_sub_category_id = None
    extrusion_sub_category_name = None
    extrusion_sub_category = None
    for builtin_def in ELEMENTS_PARAS_SUB:
        value = rParaGet.get_built_in_parameter_value(
            extrusion, builtin_def, rParaGet.get_parameter_value_as_element_id
        )
        if value != None:
            extrusion_sub_category_id = value
            extrusion_sub_category = get_category_by_id(doc, extrusion_sub_category_id)
            if extrusion_sub_category != None:
                extrusion_sub_category_name = extrusion_sub_category.Name
                
            break
    
    return extrusion_sub_category,extrusion_sub_category_id, extrusion_sub_category_name


def set_family_element_visibility_by_detail_level(doc, element, is_visible_coarse_detail):
    """
    Set the visibility of an family element by detail level.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The family element.
    :type element: Autodesk.Revit.DB.Element
    :param is_visible_coarse_detail: Set visibility for coarse detail level.
    :type is_visible_coarse_detail: bool
    :return: Result class instance.

        - `result.status` (bool): True if the visibility was set successfully, otherwise False.
        - `result.message` (str): Confirmation of successful setting of the visibility.
        - `result.result` (list): Empty
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    try:
        
        # if an element is visible in coarse detail it is not visible in fine or medium detail
        # and vise versa
        is_visible_medium_detail = not is_visible_coarse_detail
        is_visible_fine_detail = not is_visible_coarse_detail
        
        # set the visibility of the extrusion by detail level
        return_value = set_element_visibility_by_detail_level(
            doc=doc,
            element=element,
            detail_level_coarse=is_visible_coarse_detail,
            detail_level_medium=is_visible_medium_detail,
            detail_level_fine=is_visible_fine_detail,
            transaction_manager=None, # already in a transaction
        )
        
    except Exception as e:
        message = "Failed to set extrusion visibility in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value



def create_extrusion(doc, curve_loops, detail_level, height_parameter_name, source_graphic_style):
    """
    Create a new extrusion in the family document using the provided curve loops.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param curve_loops: The curve loops to use for the new extrusion.
    :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
    :param detail_level: Set visibility for coarse detail level.
    :type detail_level: bool
    :return: Result class instance.
        - `result.status` (bool): True if the extrusion was created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation of the extrusion.
        - `result.result` (list): The new extrusion element.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    try:
        
        # get the level in the family document   
        level_col = get_levels_in_model(doc)
        
        level_plane = None
        for level in level_col:
            level_plane =level
            break
        
        # set the visibility by detail level, subcategory and associate the extrusion height with the parameter
        def action(doc, extrusion):
            action_return_value = Result()
            try:
                
                # set the subcategory of the extrusion to the source extrusion sub category
                set_sub_cat_result = set_extrusion_sub_category(
                    doc=doc, 
                    extrusion=extrusion, 
                    source_graphic_style=source_graphic_style,
                    transaction_manager=None # already in a transaction,
                )
                action_return_value.update(set_sub_cat_result)
                
                # set the visibility of the extrusion by detail level
                set_result = set_family_element_visibility_by_detail_level(doc=doc, element=extrusion, is_visible_coarse_detail=detail_level)
                action_return_value.update(set_result)
                
                # associate the extrusion height with the parameter
                height_parameter_result = associate_extrusion_height_with_parameter(
                    doc=doc, 
                    extrusion=extrusion, 
                    height_parameter_name=height_parameter_name,
                    transaction_manager=None # already in a transaction
                )
                action_return_value.update(height_parameter_result)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new extrusion in family: {}".format(e))
            return action_return_value
        
        # create a new extrusion in the family document and set its visibility by detail level
        create_result = create_extrusion_on_level(doc=doc,level=level_plane, curve_loops=curve_loops, func = action)
        return_value.update(create_result)
        
    except Exception as e: 
        message = "Failed to create extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_new_extrusion_from_outlines(family_doc, curve_loops, height_parameter_name, is_visible_coarse_detail):
    """
    Create a new extrusion in the family document using the provided curve loops.
    The new extrusion will be created with the same subcategory as the existing extrusion.
    
    :param family_doc: The family document.
    :type family_doc: Autodesk.Revit.DB.Document
    :param curve_loops: The curve loops to use for the new extrusion.
    :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
    :return: Result class instance.

        - `result.status` (bool): True if the extrusion was created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation of the extrusion.
        - `result.result` (list): The new extrusion element.
        
        
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
    
    # set up a status tracker
    return_value = Result()
    try:
        # rather than updating the extrusion outline, we will delete the old extrusion and create a new one
        # need to get the category of the existing extrusion
        # cant delete an extrusion when it comes from a family template...need to create a new family from
        # an existing family not a from a template
        
        # get the existing extrusion
        generic_forms = get_all_generic_forms_in_family(family_doc)
        source_extrusion_sub_category_id = None
        source_extrusion_sub_category_name = None
        source_extrusion_sub_category = None
        source_extrusion_id = None
        
        # loop over generic forms to get the first extrusion (there should only be one)
        for el in generic_forms:
            source_extrusion_id = el.Id
            source_extrusion_sub_category,source_extrusion_sub_category_id, source_extrusion_sub_category_name = get_family_element_sub_category_id_name(family_doc, el)
            break
        
        return_value.append_message("Source extrusion sub category id: {} and name : {}".format(
            source_extrusion_sub_category_id, source_extrusion_sub_category_name))
        
        # get the graphic style of the source extrusion sub category
        source_graphic_style = get_category_graphic_style_ids(source_extrusion_sub_category)
        
        # create a new extrusion in the family document
        create_extrusion_result = create_extrusion(
            family_doc, 
            curve_loops, 
            is_visible_coarse_detail, 
            height_parameter_name=height_parameter_name,
            source_graphic_style=source_graphic_style,
        )
        return_value.update(create_extrusion_result)
        
        # get out if no extrusion was created
        if not return_value.status:
            return return_value
        
        # get the new extrusion
        element = create_extrusion_result.result[0]
        # make sure only the element is returned in the result
        return_value.result = [element]
        
        # delete the old extrusion
        if source_extrusion_id != None:
            delete_result = delete_by_element_ids(family_doc, [source_extrusion_id], "Delete source extrusion", "Extrusion")
            return_value.update(delete_result)
                
    except Exception as e:
        message = "Failed to update extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
        
    print("Return value: {}".format(return_value.message))
    return return_value



def create_curves(doc, curve_loop, detail_level,  source_graphic_style):
    """
    Create a new curves in the family document using the provided curve loops.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param curve_loop: The curve loop to use for the new extrusion.
    :type curve_loop: Autodesk.Revit.DB.CurveLoop
    :param detail_level: Set visibility for coarse detail level.
    :type detail_level: bool
    :return: Result class instance.
        - `result.status` (bool): True if the extrusion was created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation of the extrusion.
        - `result.result` (list): The new extrusion element.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    try:
        # get the level in the family document   
        level_col = get_levels_in_model(doc)
        
        level_plane = None
        for level in level_col:
            level_plane =level
            break
        
        # set the visibility by detail level, subcategory
        def action(doc, curve):
            action_return_value = Result()
            try:
                
                # set the subcategory of the symbolic curve to the source curve' sub category
                set_sub_cat_result = set_symbolic_curve_sub_category(
                    doc=doc, 
                    curve=curve, 
                    source_graphic_style=source_graphic_style,
                    transaction_manager=None # already in a transaction,
                )
                action_return_value.update(set_sub_cat_result)
                
                # set the visibility of the curve by detail level
                set_result = set_family_element_visibility_by_detail_level(doc=doc, element=curve, is_visible_coarse_detail=detail_level)
                action_return_value.update(set_result)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new curves in family: {}".format(e))
            return action_return_value
        
        # create new curves in the family document and set its visibility by detail level
        create_result = create_symbolic_curves_on_level(doc=doc,level=level_plane, curve_loop=curve_loop, func = action)
        return_value.update(create_result)
        
    except Exception as e:
        message = "Failed to create new curves in family: {}".format(e)
        return_value.update_sep(False, message)
        
    print("Return value: {}".format(return_value.message))
    return return_value
        

def add_2D_outline(family_doc, curve_loop, is_visible_coarse_detail):
    """
    Create a new curves the family document using the provided curve loops.
    The new curves will be created with the same subcategory as the existing curves.
    
    :param family_doc: The family document.
    :type family_doc: Autodesk.Revit.DB.Document
    :param curve_loops: The curve loops to use for the new extrusion.
    :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
    :return: Result class instance.

        - `result.status` (bool): True if the curves where created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation of all curves.
        - `result.result` (list): The new curve elements.
        
        
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
    
    # set up a status tracker
    return_value = Result()
    try:
        # get the existing curves
        curves = get_all_curve_based_elements_in_family(doc=family_doc)
        
        source_curves_sub_category_id = None
        source_curves_sub_category_name = None
        source_curves_sub_category = None
        source_curves_id = []
        
        # loop over curves 
        for el in curves:
            # store ids for later deletion
            source_curves_id.append(el.Id)
            source_curves_sub_category,source_curves_sub_category_id, source_curves_sub_category_name = get_family_element_sub_category_id_name(family_doc, el)
        
        return_value.append_message("Source curves sub category id: {} and name : {}".format(
            source_curves_sub_category_id, source_curves_sub_category_name))
        
        # get the graphic style of the source curves sub category
        source_graphic_style = get_category_graphic_style_ids(source_curves_sub_category)
        
        # create  new curves in the family document
        create_curves_result = create_curves(
            family_doc, 
            curve_loop, 
            is_visible_coarse_detail, 
            source_graphic_style=source_graphic_style,
        )
        return_value.update(create_curves_result)
        
        # get out if no curves where created
        if not return_value.status:
            return return_value
        
        # get the new curves
        elements = create_curves_result.result
        # make sure only the element is returned in the result
        return_value.result = elements
        
        # delete the old curves
        if source_curves_id != None and len(source_curves_id) > 0:
            delete_result = delete_by_element_ids(family_doc, source_curves_id, "Delete source curves", "Curve")
            return_value.update(delete_result)
        
        return_value.append_message("Added 2D outlines to family")
    except Exception as e:
        message = "Failed to add 2D lines in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value