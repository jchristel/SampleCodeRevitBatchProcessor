"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions for copying elements 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from Autodesk.Revit.DB import (
    IDuplicateTypeNamesHandler,
    DuplicateTypeAction,
    Transform,
    CopyPasteOptions,
    ElementTransformUtils,
    Document,
)


def copy_elements_from_target_doc(
    destination_doc, source_doc, list_of_ids, element_str
):
    """
    Copy elements from one document to another

    :param destination_doc: The document which will be the copy destination
    :type destination_doc: Document
    :param source_doc: The template document which will be the copy source
    :type source_doc: Document
    :param list_of_ids: List of element ids to copy
    :type list_of_ids: List[ElementId]
    :param element_str: String of element type to copy for logging messages
    :type element_str: str
    :return: List of new elements
    :rtype: list
    """

    class CustomCopyHandler(IDuplicateTypeNamesHandler):
        def OnDuplicateTypeNamesFound(self, args):
            return DuplicateTypeAction.UseDestinationTypes

    identity_transform = Transform.Identity
    copy_paste_opts = CopyPasteOptions()
    copy_paste_opts.SetDuplicateTypeNamesHandler(CustomCopyHandler())

    new_element_ids = ElementTransformUtils.CopyElements(
        source_doc, list_of_ids, destination_doc, identity_transform, copy_paste_opts
    )

    list_of_new_elements = []

    if new_element_ids != None:
        for id in new_element_ids:
            new_elem = destination_doc.GetElement(id)
            list_of_new_elements.append(new_elem)

    return list_of_new_elements
