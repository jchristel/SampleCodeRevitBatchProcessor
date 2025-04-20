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

from duHast.Revit.Family.family_element_utils import get_all_curve_based_elements_in_family,get_all_generic_forms_in_family
from duHast.Revit.Family.family_parameter_utils import associate_parameter_with_other_parameter_on_nested_family_instance
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Common import parameter_set_utils as rParaSet
from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_category_graphic_style_ids,
)

from duHast.Revit.Categories.Utility.category_property_names import (
    CATEGORY_GRAPHIC_STYLE_3D,
)

from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Categories.categories import (
    ELEMENTS_PARAS_SUB,
    get_category_by_id,
)

from Autodesk.Revit.DB import BuiltInParameter, CurveArrArray, CurveArray, CurveLoop, Curve, Extrusion, ModelLine ,Transaction, SketchPlane


def get_extrusion_sub_category_id_name(doc, extrusion):
    """
    Get the sub category, sub category id and subcategory name of an extrusion in a family document.
    
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
    

def set_extrusion_sub_category(doc, extrusion, source_graphic_style):
    """
    Set the subcategory of an extrusion in a family document.
    The subcategory is set to the subcategory of the source 3D graphic style.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param extrusion: The extrusion element.
    :type extrusion: Autodesk.Revit.DB.Extrusion
    :param source_graphic_style: The graphic style of the source extrusion.
    :type source_graphic_style: Autodesk.Revit.DB.GraphicStyle
    :return: Result class instance.

        - `result.status` (bool): True if the extrusion subcategory was set successfully, otherwise False.
        - `result.message` (str): Confirmation of successful setting of the extrusion subcategory.
        - `result.result` (list): The new extrusion element.
    
    
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
        
    return_value = Result()
    try:
        # assign the graphic style
        paras = extrusion.GetOrderedParameters()
        
        # flag to indicate if the value has been attempted to be set
        value_has_been_set = False
        
        # find the parameter driving the subcategory
        for p in paras:
            if p.Definition.BuiltInParameter in ELEMENTS_PARAS_SUB:
                # get the subcategory style id
                target_id = source_graphic_style[CATEGORY_GRAPHIC_STYLE_3D]
                # set the subcategory id
                updated_para = rParaSet.set_parameter_value(
                    p, str(target_id), doc
                )
                return_value.update(updated_para)
                
                # set flag to true to indicate that the value has been set, or at least attempted to be set
                value_has_been_set = True
                
                break
        if not value_has_been_set:
            return_value.update_sep(False, "Failed to set sub category in family. No parameter match found.")
    except Exception as e:
        message = "Failed to set sub category in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def set_extrusion_height_parameter(doc, extrusion, height_parameter_name):
    """
    Set the height parameter of an extrusion to a parameter in the family.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param extrusion: The extrusion element.
    :type extrusion: Autodesk.Revit.DB.Extrusion
    :param height_parameter_name: The name of the height parameter in the family.
    
    :type height_parameter_name: str
    :return: Result class instance.

        - `result.status` (bool): True if the extrusion height parameter was set successfully, otherwise False.
        - `result.message` (str): Confirmation of successful setting of the extrusion height parameter.
        - `result.result` (list): The new extrusion element.
        
    
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    try:
        # get the localised name of the height parameter
        param_extrusion_height = extrusion.get_Parameter(BuiltInParameter.EXTRUSION_END_PARAM)
        param_extrusion_height_name = param_extrusion_height.Definition.Name
        
        # set the height of the new extrusion to a parameter in the family
        attach_height_parameter_result = associate_parameter_with_other_parameter_on_nested_family_instance(
            doc=doc, 
            nested_family_instance=extrusion, 
            target_parameter_name=param_extrusion_height_name, 
            source_parameter_name=height_parameter_name,
        )
        return attach_height_parameter_result
    except Exception as e:
        message = "Failed to set extrusion height parameter in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def convert_loop_to_curve_array(curve_loop):
    """
    Convert a curve loop to a CurveArray object.
    This is used to create a new extrusion in the family document.
    
    :param curve_loop: The curve loop to convert.
    :type curve_loop: Autodesk.Revit.DB.CurveLoop
    :return: CurveArray object
    """
    
    curve_array = CurveArray()
    if (isinstance(curve_loop, CurveLoop)):
        for curve in curve_loop:
            if (isinstance(curve, Curve)):
                print("Curve: {}".format(curve))
                curve_array.Append(curve)
                
    return curve_array


def convert_curve_loops_to_curve_arr_array(curve_loops):
    """
    Convert a list of curve loops to a CurveArrArray object.
    This is used to create a new extrusion in the family document.
    
    :param curve_loops: list of curve loops
    :return: CurveArrArray object
    """
    
    # create a new curve array array
    curve_arr_array = CurveArrArray()

    curve_array = CurveArray()
    for loop in curve_loops:
        
        if (isinstance(loop, CurveLoop)):
            # a loop of curves, convert to curve array
            c_ar = convert_loop_to_curve_array(loop)
            curve_arr_array.Append(c_ar)
        elif (isinstance(loop, Curve)):
            # just a curve, not a loop
            curve_array.Append(loop)
            
    # only append the curve array if it is not empty
    if (curve_array.Size > 0):
        curve_arr_array.Append(curve_array)

    return curve_arr_array


def create_extrusion(doc, curve_loops):
    """
    Create a new extrusion in the family document using the provided curve loops.
    
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
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
    
    return_value = Result()
    try:
        # create a new extrusion
        # get the level in the family document   
        level_col = get_levels_in_model(doc)
        
        level_plane = None
        for level in level_col:
            level_plane =level
            break
            
        # convert filled region curve loops to curve array array
        new_profile = convert_curve_loops_to_curve_arr_array(curve_loops)
        
        # create a new extrusion in the family document
        def action():
       
            action_return_value = Result()
            try:
                level_reference = level_plane.GetPlaneReference()
                sketch_plane = SketchPlane.Create(doc, level_reference)
                
                # Create new extrusion
                new_extrusion = doc.FamilyCreate.NewExtrusion(True, new_profile, sketch_plane, 10.00)
                
                action_return_value.append_message("Created new extrusion in family")
                action_return_value.result.append(new_extrusion)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new extrusion in family: {}".format(e))
            return action_return_value

        transaction = Transaction(doc, "Creating extrusion")
        return_value = in_transaction(transaction,action )
    except Exception as e: 
        message = "Failed to create extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_new_extrusion_from_outlines(family_doc, curve_loops, height_parameter_name):
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
            source_extrusion_sub_category,source_extrusion_sub_category_id, source_extrusion_sub_category_name = get_extrusion_sub_category_id_name(family_doc, el)
            break
        
        return_value.append_message("Source extrusion sub category id: {} and name : {}".format(
            source_extrusion_sub_category_id, source_extrusion_sub_category_name))
        
        # get the graphic style of the source extrusion sub category
        source_graphic_style = get_category_graphic_style_ids(source_extrusion_sub_category)
        
        # create a new extrusion in the family document
        create_extrusion_result = create_extrusion(family_doc, curve_loops)
        return_value.update(create_extrusion_result)
        
        # get out if no extrusion was created
        if not return_value.status:
            return return_value
        
        # get the new extrusion
        element = create_extrusion_result.result[0]
        
        # set the sub category of the new extrusion to the source extrusion sub category
        set_sub_category_result = set_extrusion_sub_category(family_doc, element, source_graphic_style)
        return_value.update(set_sub_category_result)
        
        # set the height of the new extrusion to a parameter in the family
        attach_height_parameter_result = set_extrusion_height_parameter(family_doc, element, height_parameter_name)
        return_value.update(attach_height_parameter_result)
        
        # delete the old extrusion
        if source_extrusion_id != None:
            delete_result = delete_by_element_ids(family_doc, [source_extrusion_id], "Delete source extrusion", "Extrusion")
            return_value.update(delete_result)
                
    except Exception as e:
        message = "Failed to update extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
        
    print("Return value: {}".format(return_value.message))
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