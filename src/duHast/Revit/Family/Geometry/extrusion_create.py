"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit extrusion create helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These functions work within a Revit family document to create and manipulate extrusions.


"""
#
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
from duHast.Revit.Common.Geometry.curve_loops import convert_curve_loops_to_curve_arr_array
from duHast.Revit.Common.transaction import in_transaction

from duHast.Revit.Categories.Utility.category_property_names import CATEGORY_GRAPHIC_STYLE_3D
from duHast.Revit.Categories.categories import (
    ELEMENTS_PARAS_SUB
)

from duHast.Revit.Common.parameter_set_utils import set_parameter_value

from duHast.Revit.Family.family_parameter_utils import associate_parameter_with_other_parameter_on_nested_family_instance
from duHast.Revit.Family.Geometry.utils import set_element_sub_category
from duHast.Utilities.unit_conversion import convert_mm_to_imperial_feet

from Autodesk.Revit.DB import BuiltInParameter,Transaction, SketchPlane


def create_extrusion(doc, sketch_plane, curve_loops, func, height=100, transaction_manager=in_transaction):
    """
    Create a new extrusion in the family document using the provided curve loops.
    
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param sketch_plane: The sketch plane to use for the new extrusion.
    :type sketch_plane: Autodesk.Revit.DB.SketchPlane
    :param curve_loops: The curve loops to use for the new extrusion.
    :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
    :param func: A function to execute on the new extrusion. ( need to take the doc and the new extrusion as arguments and need to return a Result class instance)
    :type func: function
    :param transaction_manager: A function to manage transactions. (default is in_transaction)
    :type transaction_manager: function
    
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
        
        # convert filled region curve loops to curve array array
        new_profile = convert_curve_loops_to_curve_arr_array(curve_loops)
        
        # create a new extrusion in the family document
        def action():
       
            action_return_value = Result()
            try:
                # Create new extrusion
                new_extrusion = doc.FamilyCreate.NewExtrusion(True, new_profile, sketch_plane, convert_mm_to_imperial_feet(height))
                
                # check if the extrusion was created successfully
                if new_extrusion is None:
                    action_return_value.update_sep(False, "Failed to create new extrusion in family")
                else:
                    action_return_value.append_message("Created new extrusion in family")
                    
                    # execute function on extrusion
                    if func is not None:
                        func_result = func(doc, new_extrusion)
                        action_return_value.update(func_result)
                
                # add the new extrusion to the result
                action_return_value.result.append(new_extrusion)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new extrusion in family: {}".format(e))
            return action_return_value

        if transaction_manager :
            transaction = Transaction(doc, "Creating extrusion")
            return_value = transaction_manager(transaction,action )
        else:
            return_value = action()
            
    except Exception as e: 
        message = "Failed to create extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_extrusion_on_level (doc, level, curve_loops, func, height=100, transaction_manager=in_transaction):
    """
    Create a new extrusion in the family document on the level provided using the provided curve loops.

    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level to use for the new extrusion.
    :type level: Autodesk.Revit.DB.Level
    :param curve_loops: The curve loops to use for the new extrusion.
    :type curve_loops: list of Autodesk.Revit.DB.CurveLoop
    :return: Result class instance.
    :param func: A function to execute on the new extrusion. ( need to take the doc and the new extrusion as arguments and need to return a Result class instance)
    :type func: function
    :param transaction_manager: A function to manage transactions. (default is in_transaction)
    :type transaction_manager: function

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
        
        # convert filled region curve loops to curve array array
        new_profile = convert_curve_loops_to_curve_arr_array(curve_loops)
        
        # get the reference plane of the level
        level_reference = level.GetPlaneReference()
               
        # create a new extrusion in the family document
        def action():
       
            action_return_value = Result()
            try:
                
                # create a sketch plane on the level reference
                sketch_plane = SketchPlane.Create(doc, level_reference)
                 
                # Create new extrusion
                new_extrusion = doc.FamilyCreate.NewExtrusion(True, new_profile, sketch_plane, convert_mm_to_imperial_feet(height))
                
                # check if the extrusion was created successfully
                if new_extrusion is None:
                    action_return_value.update_sep(False, "Failed to create new extrusion in family")
                else:
                    action_return_value.append_message("Created new extrusion in family")
                    
                    # execute function on extrusion
                    if func is not None:
                        func_result = func(doc, new_extrusion)
                        action_return_value.update(func_result)
                
                # add the new extrusion to the result
                action_return_value.result.append(new_extrusion)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new extrusion in family: {}".format(e))
            return action_return_value

        if transaction_manager :
            transaction = Transaction(doc, "Creating extrusion")
            return_value = transaction_manager(transaction,action )
        else:
            return_value = action()
            
    except Exception as e: 
        message = "Failed to create extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value
    
    
def associate_extrusion_height_with_parameter(doc, extrusion, height_parameter_name, transaction_manager=in_transaction):
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
            transaction_manager=transaction_manager
        )
        return attach_height_parameter_result
    except Exception as e:
        message = "Failed to set extrusion height parameter in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def set_extrusion_sub_category(doc, extrusion, source_graphic_style, transaction_manager=in_transaction):
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
        - `result.result` (list): Empty.
    
    
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
        
    return_value = Result()
    try:
        return_value = set_element_sub_category(
            doc=doc,
            element=extrusion,
            source_graphic_style=source_graphic_style,
            source_graphic_style_key=CATEGORY_GRAPHIC_STYLE_3D,
            transaction_manager=transaction_manager,
        )
    except Exception as e:
        message = "Failed to set sub category in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value