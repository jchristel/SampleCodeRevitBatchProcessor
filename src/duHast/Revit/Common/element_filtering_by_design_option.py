"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Element filter by design option id's
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from duHast.Revit.Common.design_set_options import (
    get_design_option_ids_of_all_primary_options,
    get_design_option_ids_of_all_primary_options_but_the_one_containing_filter_id,
)
from Autodesk.Revit.DB import Document, ElementId, FilteredElementCollector


def filter_elements_by_design_option_id(
    doc,
    elements,
    design_option_id,
    include_main_model=True,
    include_other_primary=True,
):
    """
    Filter room separation lines by design option id.

    :param doc: The Revit document.
    :type doc: Document
    :param elements: A list of Revit elements
    :type elements: []
    :param design_option_id: The id of the design option to be filtered by. None will return either all room separation lines from the main model, if include main model is true, and / or all room separation lines from other primary design options.
    :type design_option_id: Autodesk.Revit.ElementId
    :param include_main_model: Include room separation lines from the main model option.
    :type include_main_model: bool
    :param include_other_primary: Include room separation lines from other primary design options in the model.
    :type include_other_primary: bool

    :return: A list of room separation lines filtered by design option id.
    :rtype: list
    """

    # do some type checking:
    if not isinstance(doc, Document):
        raise TypeError(
            "doc needs to be of type Document. But got : {}".format(type(doc))
        )
    if not isinstance(elements, list) and not isinstance(
        elements, FilteredElementCollector
    ):
        raise TypeError(
            "elements needs to be of type list or FilteredElementCollector. But got : {}".format(
                type(elements)
            )
        )
    if not isinstance(design_option_id, ElementId) and design_option_id != None:
        raise TypeError(
            "design_option_id needs to be of type ElementId or None. But got : {}".format(
                type(design_option_id)
            )
        )
    if not isinstance(include_main_model, bool):
        raise TypeError(
            "include_main_model needs to be of type bool. But got : {}".format(
                type(include_main_model)
            )
        )
    if not isinstance(include_other_primary, bool):
        raise TypeError(
            "include_other_primary needs to be of type bool. But got : {}".format(
                type(include_other_primary)
            )
        )

    # set up a place holder to hold design option ids to filter by
    option_ids = []
    # get the design option filter ids depending on toggle values and filter id past in
    if (
        design_option_id == None
        and include_main_model == True
        and include_other_primary == True
    ):
        # return lines within the main model and other primary design options
        # get all primary design option ids
        ids_all_primary = get_design_option_ids_of_all_primary_options(doc)
        option_ids.extend(ids_all_primary)
        # add the main model id
        option_ids.append(ElementId.InvalidElementId)
    elif (
        design_option_id == None
        and include_main_model == False
        and include_other_primary == True
    ):
        # return lines within other primary design options only
        # get all primary design option ids
        ids_all_primary = get_design_option_ids_of_all_primary_options(doc)
        option_ids.extend(ids_all_primary)
    elif (
        design_option_id == None
        and include_main_model == True
        and include_other_primary == False
    ):
        # return lines within the main model only
        option_ids.append(ElementId.InvalidElementId)
    elif (
        design_option_id == None
        and include_main_model == False
        and include_other_primary == False
    ):
        # nothing to be returned? Throw an error
        raise ValueError("You need to include at least one option to filter by.")
    elif (
        design_option_id != None
        and include_main_model == True
        and include_other_primary == True
    ):
        # return lines within the specified design option, the main model and other primary design options
        # get all primary design option ids except the one where the design set contains the design option filter id
        ids_primary_filtered = get_design_option_ids_of_all_primary_options_but_the_one_containing_filter_id(
            doc=doc, filter_id=design_option_id
        )
        option_ids.extend(ids_primary_filtered)
        # add the design option filter id
        option_ids.append(design_option_id)
        # add the main model id
        option_ids.append(ElementId.InvalidElementId)
    elif (
        design_option_id != None
        and include_main_model == False
        and include_other_primary == True
    ):
        # return lines within the specified design option and other primary design options only
        # get all primary design option ids except the one where the design set contains the design option filter id
        ids_primary_filtered = get_design_option_ids_of_all_primary_options_but_the_one_containing_filter_id(
            doc=doc, filter_id=design_option_id
        )
        option_ids.extend(ids_primary_filtered)
        # add the design option filter id
        option_ids.append(design_option_id)
    elif (
        design_option_id != None
        and include_main_model == True
        and include_other_primary == False
    ):
        # return lines within the specified design option and the main model only
        # add the design option filter id
        option_ids.append(design_option_id)
        # add the main model id
        option_ids.append(ElementId.InvalidElementId)
    elif (
        design_option_id != None
        and include_main_model == False
        and include_other_primary == False
    ):
        # return lines within the specified design option only
        option_ids.append(design_option_id)

    # set up a return value
    elements_filtered = []

    # loop over lines and filter them by design option id
    for element_instance in elements:
        try:
            # check if the design option id of the element is in the list of design option ids
            element_design_option = element_instance.DesignOption
            # main model is represented by an invalid element id in the design option ;list
            # however on the element its represented by None
            if element_design_option is not None:
                if element_instance.DesignOption.Id in option_ids:
                    elements_filtered.append(element_instance)
            else:
                if ElementId.InvalidElementId in option_ids:
                    elements_filtered.append(element_instance)
        except Exception as e:
            raise ValueError(
                "Error while filtering elements by design option id. Error: {}".format(
                    e
                )
            )

    # return filtered set
    return elements_filtered
