"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit purging not used line pattern styles using purge by delete helper functions. 
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

from duHast.Revit.LinePattern.line_patterns import get_all_line_patterns
from duHast.Revit.Common.common import get_ids_from_element_collector
from duHast.Revit.Purge.purge_unused_by_delete import purge_unused_elements
from duHast.Revit.Categories.categories_styles_model import (
    get_category_styles,
    get_all_used_line_patterns_ids_from_categories,
)

from duHast.Utilities.Objects.result import Result


def get_line_pattern_ids(doc, element_ids=None, element_ids_list_is_inclusive_filter=True):
    """
    Returns all line pattern ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_ids: optional list of shared parameter element ids
    :type element_ids: [Autodesk.Revit.DB.ElementId]
    :param element_ids_list_is_inclusive_filter: If true and element_ids list has values only those line patterns will be purged if possible. If false and element_ids list has values any line patterns in the list will not be purged.
    :type element_ids_list_is_inclusive_filter: bool

    :return: A list of all line pattern ids in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    line_pattern_col = get_all_line_patterns(doc)
    ids = get_ids_from_element_collector(line_pattern_col)

    # do some pre -purge filtering
    # remove all line patterns that are used in categories
    categories_result = get_category_styles(doc)
    if categories_result.status == False:
        return ids
    
    category_styles = categories_result.result

    # get line patterns used in categories
    used_line_pattern_ids = get_all_used_line_patterns_ids_from_categories(
        category_styles
    )

    # remove used line patterns
    ids_not_used = [x for x in ids if x.IntegerValue not in used_line_pattern_ids]

    # check if further filtering is required
    if element_ids is None:
        return ids_not_used
    
    # apply filtering
    ids_filtered = []
    if element_ids_list_is_inclusive_filter:
        # only return element ids which are also present in the filter list
        for id_not_used in ids_not_used:
            if id_not_used in element_ids:
                ids_filtered.append(id_not_used)
    else:
        # only return element ids which are not present in the filter list
        for id_not_used in ids_not_used:
            if id_not_used not in element_ids:
                ids_filtered.append(id_not_used)
    
    return ids_filtered


def purge_line_pattern_by_delete(doc, progress_callback=None, debug=False, element_ids=None, element_ids_list_is_inclusive_filter=True):
    """
    Purge line pattern by delete.

    Note: This is a very slow process and can take a few hours to complete depending on the size of the model and the number of line patterns.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param progress_callback: Callback to report progress.
    :type progress_callback: callable
    :param debug: Debug mode.
    :type debug: bool
    :param element_ids: optional list of shared parameter element ids
    :type element_ids: [Autodesk.Revit.DB.ElementId]
    :param element_ids_list_is_inclusive_filter: If true and element_ids list has values only those parameters will be purged if possible. If false and element_ids list has values any parameters in the list will not be purged.
    :type element_ids_list_is_inclusive_filter: bool
    
    :return: Result class instance.

        - .status True if unused line pattern where deleted or nothing needed to be deleted. Otherwise False.
        - .message will contain deletion status.

    """

    return_value = Result()

    try:

        # set up element Id getter
        # make allowance for an ignore element id list
        def action(doc):
            result_action = get_line_pattern_ids(
                doc=doc, element_ids=element_ids,
                element_ids_list_is_inclusive_filter=element_ids_list_is_inclusive_filter
            )
            return result_action
        
        # purge unused fill patterns
        purge_result = purge_unused_elements(
            doc=doc,
            element_id_getter=action,
            deleted_elements_modifier=None,
            modified_elements_modifier=None,
            progress_callback=progress_callback,
            debug=debug,
        )

        return_value.update(purge_result)
    except Exception as e:
        return_value.update_sep(
            False, "Error purging line pattern by delete: {}".format(str(e))
        )

    return return_value
