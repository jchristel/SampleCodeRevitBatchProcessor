"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module to provide pyRevit UI helpers for selecting a Revit document (active or linked).
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


from duHast.Revit.Links.links import get_link_docs
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user


def get_docs_for_selection(doc):
    """
    Returns a list containing the active document followed by all loaded linked documents.

    :param doc: The active Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of documents available for selection.
    :rtype: list[Autodesk.Revit.DB.Document]
    """
    docs = [doc]
    link_docs = get_link_docs(doc, link_names_filter=[], inverse_filter=True)
    for _, link_doc in link_docs.items():
        docs.append(link_doc)
    return docs


def _doc_name_builder(element):
    """
    Returns the document title for display in the selection UI.

    :param element: A Revit document.
    :type element: Autodesk.Revit.DB.Document
    :return: Document title.
    :rtype: str
    """
    return element.Title


def pick_document(doc, forms, button_name="Select document", multiselect=False):
    """
    Prompts the user to select a Revit document (active or linked) via a pyRevit SelectFromList dialog.

    :param doc: The active Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: The pyRevit forms module.
    :type forms: module
    :param button_name: Label on the selection button.
    :type button_name: str
    :param multiselect: Allow selecting multiple documents.
    :type multiselect: bool
    :return: The selected document, a list of selected documents, or None if cancelled.
    :rtype: Autodesk.Revit.DB.Document or list[Autodesk.Revit.DB.Document] or None
    """
    selected = get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=get_docs_for_selection,
        element_selection_description=button_name,
        multiselect=multiselect,
        ui_element_name_builder=_doc_name_builder,
    )

    if not selected:
        return None

    return selected if multiselect else selected[0]
