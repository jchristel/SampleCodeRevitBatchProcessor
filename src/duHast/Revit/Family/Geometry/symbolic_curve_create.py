"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit symbolic curve create helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These functions work within a Revit family document to create and manipulate symbolic curves.


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
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Categories.categories import (
    ELEMENTS_PARAS_SUB
)

from duHast.Revit.Family.Geometry.utils import set_curve_sub_category

from Autodesk.Revit.DB import Curve, Transaction, SketchPlane

def create_symbolic_curves_by_curve_loop(doc, sketch_plane, curve_loop, func, transaction_manager=in_transaction):
    """
    Create new symbolic curves in the family document using the provided curve loop.
    
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param sketch_plane: The sketch plane to use for the new curve(s).
    :type sketch_plane: Autodesk.Revit.DB.SketchPlane
    :param curve_loop: The curve loop to use for the new curve(s).
    :type curve_loop:  Autodesk.Revit.DB.CurveLoop
    :param func: A function to execute on the new curves. ( need to take the doc and  a single new curves as arguments and need to return a Result class instance)
    :type func: function
    :param transaction_manager: A function to manage transactions. (default is in_transaction)
    :type transaction_manager: function
    
    :return: Result class instance.

        - `result.status` (bool): True if the symbolic curves where created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation of the symbolic curves.
        - `result.result` (list): The new symbolic curve elements.
        
    On exception:
    
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    try:
        
        # create new symbolic curves in the family document
        def action():
       
            action_return_value = Result()
            try:
                # Create new curves from the curve loop
                for curve in curve_loop:
                    
                    # check if the curve is a valid Curve object
                    if (not isinstance(curve, Curve)):
                        action_return_value.update_sep(False, "Element is not a valid Curve object: {}".format(type(curve)))
                        continue
                    
                    new_curve = doc.FamilyCreate.NewSymbolicCurve(curve, sketch_plane)
                
                    # check if the curve was created successfully
                    if new_curve is None:
                        action_return_value.update_sep(False, "Failed to create new curve in family")
                    else:
                        action_return_value.append_message("Created new curve in family")
                    
                    # execute function on symbolic curve
                    if func is not None:
                        func_result = func(doc, new_curve)
                        action_return_value.update(func_result)
                
                    # add the new symbolic curve to the result
                    action_return_value.result.append(new_curve)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new curve(s) in family: {}".format(e))
            return action_return_value

        if transaction_manager :
            transaction = Transaction(doc, "Creating symbolic curves")
            return_value = transaction_manager(transaction,action )
        else:
            return_value = action()
            
    except Exception as e: 
        message = "Failed to create symbolic curves in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def create_symbolic_curves_on_level (doc, level, curve_loop, func, transaction_manager=in_transaction):
    """
    Create a new symbolic curves in the family document on the level provided using the provided curve loop.

    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level to use for the new symbolic curves.
    :type level: Autodesk.Revit.DB.Level
    :param curve_loops: The curve loop to use for the new symbolic curves.
    :type curve_loops: Autodesk.Revit.DB.CurveLoop
    :param func: A function to execute on the new symbolic curves. ( need to take the doc and a new symbolic curve as arguments and need to return a Result class instance)
    :type func: function
    :param transaction_manager: A function to manage transactions. (default is in_transaction)
    :type transaction_manager: function

        - `result.status` (bool): True if the symbolic curves where created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation of the symbolic curves.
        - `result.result` (list): The new symbolic curve elements.
    
    On exception:
    
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    try:
        
        # get the reference plane of the level
        level_reference = level.GetPlaneReference()
               
        # create a new symbolic curves in the family document
        def action():
       
            action_return_value = Result()
            try:
                # Create new curves from the curve loop
                for curve in curve_loop:
                    
                    # check if the curve is a valid Curve object
                    if (not isinstance(curve, Curve)):
                        action_return_value.update_sep(False, "Element is not a valid Curve object: {}".format(type(curve)))
                        continue
                    
                    # create a sketch plane on the level reference
                    sketch_plane = SketchPlane.Create(doc, level_reference)
                    
                    # Create new symbolic curves
                    new_curve = doc.FamilyCreate.NewSymbolicCurve(curve, sketch_plane)
                    
                    # check if the symbolic curves was created successfully
                    if new_curve is None:
                        action_return_value.update_sep(False, "Failed to create new symbolic curve in family")
                    else:
                        action_return_value.append_message("Created new symbolic curve in family")
                        
                        # execute function on symbolic curves
                        if func is not None:
                            func_result = func(doc, new_curve)
                            action_return_value.update(func_result)
                    
                    # add the new symbolic curve to the result
                    action_return_value.result.append(new_curve)
                
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create new symbolic curves in family: {}".format(e))
            return action_return_value

        if transaction_manager :
            transaction = Transaction(doc, "Creating symbolic curves")
            return_value = transaction_manager(transaction,action )
        else:
            return_value = action()
            
    except Exception as e: 
        message = "Failed to create symbolic curves in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def set_symbolic_curve_sub_category(doc, curve, source_graphic_style, transaction_manager=in_transaction):
    """
    Set the subcategory of an symbolic curve in a family document.
    The subcategory is set to the subcategory of the source projection graphic style.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param curve: The curve element.
    :type curve: Autodesk.Revit.DB.Curve
    :param source_graphic_style: The graphic style of the source curve.
    :type source_graphic_style: Autodesk.Revit.DB.GraphicStyle
    :return: Result class instance.

        - `result.status` (bool): True if the curve subcategory was set successfully, otherwise False.
        - `result.message` (str): Confirmation of successful setting of the curve subcategory.
        - `result.result` (list): Empty.
    
    
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
        
    return_value = Result()
    try:
        return_value = set_curve_sub_category(
            doc=doc, 
            element=curve, 
            source_graphic_style=source_graphic_style, 
            transaction_manager=transaction_manager,
        )
    except Exception as e:
        message = "Failed to set curve sub category in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value