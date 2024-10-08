"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit purging not used line styles by using the purge by delete helper functions. 
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

from duHast.Revit.LinePattern.line_styles import get_all_line_style_ids
from duHast.Revit.Common.common import get_ids_from_element_collector
from duHast.Revit.Purge.purge_unused_by_delete import purge_unused_elements
from duHast.Revit.LinePattern.Objects.LineStylePurgeModifier import (
    LineStylePurgeModifier,
)
from duHast.Utilities.Objects.result import Result

def get_line_style_ids(doc, element_ids=None, element_ids_list_is_inclusive_filter=True):
    """
    Returns all line style ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_ids: optional list of line style element ids
    :type element_ids: [Autodesk.Revit.DB.ElementId]
    :param element_ids_list_is_inclusive_filter: If true and element_ids list has values only those line styles will be purged if possible. If false and element_ids list has values any line styles in the list will not be purged.
    :type element_ids_list_is_inclusive_filter: bool

    :return: A list of all line styles ids in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    line_pattern_col = get_all_line_style_ids(doc)
    ids = get_ids_from_element_collector(line_pattern_col)

    # check if filtering is required
    if (element_ids is None):
        return ids
    
    # apply filtering
    ids_filtered = []
    if element_ids_list_is_inclusive_filter:
        # only return element ids which are also present in the filter list
        for id in ids:
            if id in element_ids:
                ids_filtered.append(id)
    else:
        # only return element ids which are not present in the filter list
        for id in ids:
            if id not in element_ids:
                ids_filtered.append(id)
    
    return ids_filtered


def purge_line_styles_by_delete(doc, progress_callback=None, debug=False, element_ids=None, element_ids_list_is_inclusive_filter=True):
    """
    Purge line styles by delete.

    Note: This is a quick(ish) process and can take a few minutes to complete depending on the size of the model and the number of line styles.

    Observations:

    - when deleting a line style in Revit, the associated graphics style will be deleted as well. Which leads to a minimum of 2 deleted elements per line style.
    - a custom element deleted modifier is used to check if the deleted element count is 2 and if the second deleted element is the associated graphics style.
    - if that is the case and no modified elements are listed, the deleted element count is reduced to 1 and the line style is considered as deleted.


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param progress_callback: Callback to report progress.
    :type progress_callback: callable
    :param debug: Debug mode.
    :type debug: bool
    :param element_ids: optional list of line style element ids
    :type element_ids: [Autodesk.Revit.DB.ElementId]
    :param element_ids_list_is_inclusive_filter: If true and element_ids list has values only those line styles will be purged if possible. If false and element_ids list has values any line styles in the list will not be purged.
    :type element_ids_list_is_inclusive_filter: bool

    :return: Result class instance.

        - .status True if unused line styles where deleted or nothing needed to be deleted. Otherwise False.
        - .message will contain deletion status.

    """

    return_value = Result()

    try:

        # set up element Id getter
        # make allowance for an ignore element id list
        def action(doc):
            result_action = get_line_style_ids(
                doc=doc, element_ids=element_ids,
                element_ids_list_is_inclusive_filter=element_ids_list_is_inclusive_filter
            )
            return result_action
        
        # set up delete modifier instance
        # reduces the count of deleted elements to the line style only by removing the associated graphics style
        mod_delete = LineStylePurgeModifier(doc)

        # purge unused line styles
        purge_result = purge_unused_elements(
            doc=doc,
            element_id_getter=action,
            deleted_elements_modifier=mod_delete,
            modified_elements_modifier=None,
            progress_callback=progress_callback,
            debug=debug,
        )

        # get the debug log if debug mode is enabled
        if debug:
            return_value.append_message("\n".join(mod_delete.debug_log))

        return_value.update(purge_result)
    except Exception as e:
        return_value.update_sep(
            False, "Error purging line styles by delete: {}".format(str(e))
        )

    return return_value
