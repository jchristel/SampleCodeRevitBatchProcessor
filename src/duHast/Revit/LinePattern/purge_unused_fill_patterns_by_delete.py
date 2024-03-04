"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit purging not used fill pattern styles using purge by delete helper functions. 
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

from duHast.Revit.LinePattern.fill_patterns import get_all_fill_pattern
from duHast.Revit.Common.common import get_ids_from_element_collector
from duHast.Revit.Purge.purge_unused_by_delete import purge_unused_elements

from duHast.Utilities.Objects.result import Result


def get_fill_pattern_ids(doc):
    """
    Returns all fill pattern ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of all fill pattern ids in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    fill_pattern_col = get_all_fill_pattern(doc)
    ids = get_ids_from_element_collector(fill_pattern_col)
    return ids

def purge_fill_pattern_by_delete(doc, progress_callback=None, debug=False):
    """
    Purge fill pattern by delete.

    Note: This is a very slow process and can take a few hours to complete depending on the size of the model and the number of fill patterns.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param progress_callback: Callback to report progress.
    :type progress_callback: callable
    :param debug: Debug mode.
    :type debug: bool
    :return: Result class instance.

        - .status True if unused fill pattern where deleted or nothing needed to be deleted. Otherwise False.
        - .message will contain deletion status.

    """

    return_value = Result()

    try:

        # purge unused fill patterns
        purge_result = purge_unused_elements(
            doc=doc,
            element_id_getter=get_fill_pattern_ids,
            deleted_elements_modifier=None,
            modified_elements_modifier=None,
            progress_callback=progress_callback,
            debug=debug,
        )

        return_value.update(purge_result)
    except Exception as e:
        return_value.update_sep(
            False, "Error purging fill pattern by delete: {}".format(str(e))
        )

    return return_value