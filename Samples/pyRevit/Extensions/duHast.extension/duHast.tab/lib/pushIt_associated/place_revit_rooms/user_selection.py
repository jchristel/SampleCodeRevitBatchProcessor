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
from duHast.Revit.Links.links import get_link_docs



def get_models_for_selection(doc):

    docs = [doc]
     # get all linked models
    link_docs = get_link_docs(doc, link_names_filter=[])

    for link_doc in link_docs:
        # add the linked model to the list
        docs.append(link_doc)

    return docs


def ui_doc_name_builder(element):
    return element.Title


def get_model_selection_from_user(doc, forms, element_getter, element_selection_description, multiselect = True, ui_element_name_builder = ui_doc_name_builder):
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
    :rtype: None or [Autodesk.Revit.Element]
    """
    # set up return values
    element_names = []
    elements_by_name = {}

    # get all elements from the getter
    elements = element_getter(doc=doc)
    
    # check if we got any?
    if elements is None or len(elements) == 0:
        return None

    for element in elements:
        # check if this is an element id rather than an element
        key = ui_element_name_builder(element=element)
        element_names.append(key)
        if(key in elements_by_name):
            print("Warning element {} exists twice in the model!".format(key))
        elements_by_name[key] = element
    
    elements_selected = None

    # check if we got any?
    if(len(element_names)==0):
        print("No elements left to display")
        return elements_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(sorted(element_names), button_name='{}'.format(element_selection_description), multiselect= multiselect)
    
    if(selection == None):
        return elements_selected
    else:
        elements_selected = []
        # check if string ( single selection) or list ( multiple selection)
        if(isinstance(selection, str)):
            elements_selected.append(elements_by_name[selection])
            return elements_selected
        else:
            for element_key_name in selection:
                elements_selected.append(elements_by_name[element_key_name])
            return elements_selected


def get_model_selection(doc, forms):

    doc_selected = get_model_selection_from_user(
        doc=doc, 
        forms=forms, 
        element_getter= get_models_for_selection, 
        element_selection_description ="Select model with push it rooms.",
          multiselect = False, 
          ui_element_name_builder = ui_doc_name_builder
    )

    # check if the user selected a model
    if doc_selected is not None and len(doc_selected) > 0:
        # get the selected model
        selected_model = doc_selected[0]

        return  selected_model
    else:
        # if the user cancelled the selection, return None
        return None