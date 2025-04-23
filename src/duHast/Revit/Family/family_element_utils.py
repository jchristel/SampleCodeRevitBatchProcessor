"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions retrieving elements from a family.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from Autodesk.Revit.DB import (
    CurveElement,
    Element,
    FamilyElementVisibility,
    FamilyElementVisibilityType,
    FilteredElementCollector,
    GenericForm,
    ModelText,
    ReferencePlane,
    Transaction,
)

LINE_NAMES = [
    "Model Lines",  # 3D families
    "Symbolic Lines",  # 3D families
    "Line",  # annotation (tag) families
]


def get_all_generic_forms_in_family(doc):
    """
    Filters all generic forms (3D extrusions) in family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector of Autodesk.Revit.DB.GenericForm.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = FilteredElementCollector(doc).OfClass(GenericForm)
    return col


def get_all_curve_based_elements_in_family(doc):
    """
    Filters all curve-based elements in a family, including symbolic lines and model lines.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of Autodesk.Revit.DB.CurveElement.
    :rtype: list of Autodesk.Revit.DB.CurveElement
    """

    elements = []
    col = FilteredElementCollector(doc).OfClass(CurveElement)
    for c in col:
        if Element.Name.GetValue(c) in LINE_NAMES:
            elements.append(c)
    return elements


def get_all_model_text_elements_in_family(doc):
    """
    Filters all model text elements in family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector of Autodesk.Revit.DB.ModelText.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = FilteredElementCollector(doc).OfClass(ModelText)
    return col


def get_all_reference_planes_in_family(doc):
    """
    Filters all reference planes in family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector of Autodesk.Revit.DB.ReferencePlane.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = FilteredElementCollector(doc).OfClass(ReferencePlane)
    return col


def set_element_visibility_by_detail_level(
        doc, 
        element, 
        detail_level_coarse = True,  
        detail_level_medium = True, 
        detail_level_fine = True, 
        family_element_visibility_type =  FamilyElementVisibilityType.Model, 
        transaction_manager= in_transaction
    ):
    
    """
    Set the visibility of an element by detail level.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The element to set the visibility for.
    :type element: Autodesk.Revit.DB.Element
    :param detail_level_coarse: Set visibility for coarse detail level.
    :type detail_level_coarse: bool
    :param detail_level_fine: Set visibility for fine detail level.
    :type detail_level_fine: bool
    :param detail_level_medium: Set visibility for medium detail level.
    :type detail_level_medium: bool
    :param family_element_visibility_type: The type of visibility to set. (Model vs View specific)
    :type family_element_visibility_type: Autodesk.Revit.DB.FamilyElementVisibilityType
    
    :return: Result class instance.

        - `result.status` (bool): True if the visibility was updated successfully, otherwise False.
        - `result.message` (str): Confirmation of successful application of visibility settings.
        - `result.result` (list): Empty.
        
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
        
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    
    try:
        
        def action():
            action_return_value = Result()
            try:
                fam_element_visibility = FamilyElementVisibility(family_element_visibility_type)

                # Set visibility options
                fam_element_visibility.IsShownInCoarse = detail_level_coarse
                fam_element_visibility.IsShownInMedium = detail_level_medium   
                fam_element_visibility.IsShownInFine = detail_level_fine

                # Apply visibility settings to the extrusion
                element.SetVisibility(fam_element_visibility)

                action_return_value.append_message("Visibility set by detail level fine: {} medium: {} coarse: {}".format(detail_level_fine, detail_level_medium, detail_level_coarse))
            except Exception as e:
                action_return_value.update_sep(False, "Error setting visibility by detail level: {}".format(e))
            return action_return_value
        
        # check if this need to be run inside a transaction
        if transaction_manager:
            # If a transaction manager is provided, create a new transaction
            transaction = Transaction(doc, "Setting detail level visibility")
            return_value = transaction_manager(transaction,action )
        else:
            # If no transaction manager is provided, run the action without a transaction
            # assuming there is one already in place
            return_value = action()
        
    except Exception as e:
        return_value.update_sep(False, "Error setting visibility by detail level: {}".format(e))
    
    return return_value