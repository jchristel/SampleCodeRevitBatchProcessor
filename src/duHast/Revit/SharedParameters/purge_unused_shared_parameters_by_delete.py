"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit purging not used shared parameters using purge by delete helper functions. 
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

from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters
from duHast.Revit.Common.common import get_ids_from_element_collector
from duHast.Revit.Purge.purge_unused_by_delete import purge_unused_elements

from duHast.Utilities.Objects.result import Result


def get_shared_parameter_ids(doc):
    """
    Returns all shared parameter ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of all shared parameter ids in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    shared_col = get_all_shared_parameters(doc)
    ids = get_ids_from_element_collector(shared_col)
    return ids

def purge_shared_parameters_by_delete(doc, progress_callback=None, debug=False):
    """
    Purge shared parameters by delete.

    Note: This is a slow(ish) process and can take a few hours to complete depending on the size of the model and the number of shared parameters.

    No parameters with a category binding will be deleted. (refer below for more details on this)

    Observations:

    - any shared parameter which is bound to a category in a Revit model (but not used in a family etc) will report 2 elements as deleted:
        - the shared parameter itself
        - the binding (type or instance) to a category
    
    - any shared parameter which is not bound to a category in a Revit model, but used in a family etc will report 
        - 1 element as deleted
            - the shared parameter itself
        - multiple changed elements: 
            - the families (and any of its instances placed) the shared parameter is used in

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param progress_callback: Callback to report progress.
    :type progress_callback: callable
    :param debug: Debug mode.
    :type debug: bool
    :return: Result class instance.

        - .status True if unused shared parameters where deleted or nothing needed to be deleted. Otherwise False.
        - .message will contain deletion status.

    """

    return_value = Result()

    try:

        # purge unused shared parameters
        purge_result = purge_unused_elements(
            doc=doc,
            element_id_getter=get_shared_parameter_ids,
            deleted_elements_modifier=None,
            modified_elements_modifier=None,
            progress_callback=progress_callback,
            debug=debug,
        )

        return_value.update(purge_result)
    except Exception as e:
        return_value.update_sep(
            False, "Error purging shared parameters by delete: {}".format(str(e))
        )

    return return_value
