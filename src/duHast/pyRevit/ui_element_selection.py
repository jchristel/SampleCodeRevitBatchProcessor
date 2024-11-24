"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to py Revit element selection from list. 
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



from Autodesk.Revit.DB import ElementId


def default_name_builder (element):
    """
    Deafult element name builder is used to build the element name shown in the UI by combining the element name and element  Id

    :param element: An element
    :type element: Autodesk.Revit.DB.Element
    :return: A name of the element.
    :rtype: str
    """
    key = "{} ({})".format(element.Name, element.Id)
    return key


def get_element_selection_from_user(doc, forms, element_getter, element_selection_description, multiselect = True, ui_element_name_builder = default_name_builder):
    """
    lists Elements provided by element getter function in UI and returns the users selection

    :param doc: Ther current Revit model.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms
    :type forms: _type_
    :param element_getter: Function accpeting the document as the only argument returning a list of elements or empty list.
    :type element_getter: _type_
    :param element_selection_description: Text to be displayes on button to prompt user
    :type element_selection_description: str
    
    :return: None if nothing was selected. Otherwise a list of element ids
    :rtype: None or [Autodesk.Revit.ElementId]
    """
    # set up return values
    element_names = []
    elements_by_name = {}

    # get all view templates
    elements = element_getter(doc=doc)
    for element in elements:
        # check if this is an element id rather than an element
        if isinstance(element, ElementId):
            element = doc.GetElement(element)
        key = ui_element_name_builder(element=element)
        element_names.append(key)
        if(key in elements_by_name):
            print("Warning element {} exists twice in the model!".format(key))
        elements_by_name[key] = element
    
    elements_selected = None

    # check if we got any?
    if(len(element_names)==0):
        return elements_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(sorted(element_names), button_name='{}'.format(element_selection_description), multiselect= multiselect)
    
    if(selection == None):
        return elements_selected
    else:
        elements_selected = []
        for element_key_name in selection:
            elements_selected.append(elements_by_name[element_key_name].Id)
        return elements_selected