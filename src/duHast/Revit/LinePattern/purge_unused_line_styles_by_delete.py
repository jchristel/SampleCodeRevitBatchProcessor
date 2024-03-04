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
from duHast.Revit.Purge.purge_unused_by_delete import purge_unused_elements
from duHast.Revit.LinePattern.Objects.LineStylePurgeModifier import (
    LineStylePurgeModifier,
)
from duHast.Utilities.Objects.result import Result


def purge_line_styles_by_delete(doc, progress_callback=None, debug=False):
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
    :return: Result class instance.

        - .status True if unused line styles where deleted or nothing needed to be deleted. Otherwise False.
        - .message will contain deletion status.

    """

    return_value = Result()

    try:
        # set up delete modifier instance
        mod_delete = LineStylePurgeModifier(doc)

        # purge unused line styles
        purge_result = purge_unused_elements(
            doc=doc,
            element_id_getter=get_all_line_style_ids,
            deleted_elements_modifier=mod_delete, # reduces the count of deleted elements to the line style only by removing the associated graphics style
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