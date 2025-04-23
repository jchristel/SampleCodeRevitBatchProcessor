"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit common family element helper functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These functions work within a Revit family document to create and manipulate elements.


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
from duHast.Revit.Categories.Utility.category_property_names import CATEGORY_GRAPHIC_STYLE_PROJECTION
from duHast.Revit.Categories.categories import (
    ELEMENTS_PARAS_SUB
)

from duHast.Revit.Common.parameter_set_utils import set_parameter_value

def set_element_sub_category(doc, element, source_graphic_style, source_graphic_style_key, transaction_manager=in_transaction):
    """
    Set the subcategory of an element in a family document.
    The subcategory is set to the subcategory of the source projection graphic style.
    
    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The element.
    :type element: Autodesk.Revit.DB.Element
    :param source_graphic_style: The graphic style of the source curve.
    :type source_graphic_style: Autodesk.Revit.DB.GraphicStyle
    :param source_graphic_style_key: The key of the graphic style to set. (e.g. "Projection", "Cut", "3D")
    :type source_graphic_style_key: str
    :return: Result class instance.

        - `result.status` (bool): True if the elements subcategory was set successfully, otherwise False.
        - `result.message` (str): Confirmation of successful setting of the elements subcategory.
        - `result.result` (list): Empty.
    
    
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
        
    return_value = Result()
    try:
        # assign the graphic style
        paras = element.GetOrderedParameters()
        
        # flag to indicate if the value has been attempted to be set
        value_has_been_set = False
        
        # find the parameter driving the subcategory
        for p in paras:
            if p.Definition.BuiltInParameter in ELEMENTS_PARAS_SUB:
                # get the subcategory style id
                target_id = source_graphic_style[ source_graphic_style_key]
                # set the subcategory id
                updated_para = set_parameter_value(
                    p, 
                    str(target_id), 
                    doc,
                    transaction_manager
                )
                return_value.update(updated_para)
                
                # set flag to true to indicate that the value has been set, or at least attempted to be set
                value_has_been_set = True
                
                break
        if not value_has_been_set:
            return_value.update_sep(False, "Failed to set sub category of element in family. No parameter match found.")
    except Exception as e:
        message = "Failed to set sub category of element in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value


def set_curve_sub_category(doc, element, source_graphic_style, transaction_manager=in_transaction):
    """
    Set the subcategory of a curve in a family document. ( its really the graphic style...)
    The subcategory is set to the subcategory of the source projection graphic style.

    :param doc: The family document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The element.
    :type element: Autodesk.Revit.DB.Element
    :param source_graphic_style: The graphic style of the source curve.
    :type source_graphic_style: Autodesk.Revit.DB.GraphicStyle
    :param transaction_manager: The transaction manager.
    :type transaction_manager: function

    :return: Result class instance.
        - `result.status` (bool): True if the elements subcategory was set successfully, otherwise False.
        - `result.message` (str): Confirmation of successful setting of the elements subcategory.
        - `result.result` (list): Empty.
    On exception:

        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        # assign the graphic style
        paras = element.GetOrderedParameters()
        
        # flag to indicate if the value has been attempted to be set
        value_has_been_set = False
        
        # find the parameter driving the subcategory
        for p in paras:
            if p.Definition.BuiltInParameter in ELEMENTS_PARAS_SUB:
                # get the subcategory style id
                target_id = source_graphic_style.Id
                # set the subcategory id
                updated_para = set_parameter_value(
                    p, 
                    str(target_id), 
                    doc,
                    transaction_manager
                )
                return_value.update(updated_para)
                
                # set flag to true to indicate that the value has been set, or at least attempted to be set
                value_has_been_set = True
                
                break
        if not value_has_been_set:
            return_value.update_sep(False, "Failed to set sub category of element in family. No parameter match found.")
    except Exception as e:
        message = "Failed to set sub category of element in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value