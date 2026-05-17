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
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.SharedParameters.purge_unused_shared_parameters_by_delete import (
    purge_shared_parameters_by_delete,
)
from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user


def purge_shared_parameters(doc, output, forms):
    """
    Purges all unused shared parameters from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if shared parameters where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Shared Parameters: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_shared_parameters_by_delete(
            doc=doc, progress_callback=progress_callback, debug=True
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(purge_status)

    print("Finished.")

    return return_value


def _name_builder_for_ui(element):
    """
    Shared Parameter name builder which is used to build the element name shown in the UI by combining the element name and element  GUID

    :param element: An element
    :type element: Autodesk.Revit.DB.Element
    :return: A name of the element.
    :rtype: str
    """
    key = "{} ({})".format(element.Name, element.GuidValue)
    return key


def purge_shared_parameters_by_selection(doc, output, forms):
    """
    Purges all unused shared parameters from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if selected shared parameters where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get user to select which parameters to purge
    selected_shared_parameter_ids = get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=get_all_shared_parameters,
        element_selection_description="Select Shared Parameters To Purge",
        ui_element_name_builder=_name_builder_for_ui,
    )

    # check if anything was selected
    if selected_shared_parameter_ids == None or len(selected_shared_parameter_ids) == 0:
        return_value.update_sep(False, "No parameters to purge where selected.")
        print("{}\nFinished.".format(return_value.message))
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Purging Shared Parameters: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # purge it
        purge_status = purge_shared_parameters_by_delete(
            doc=doc,
            progress_callback=progress_callback,
            debug=True,
            element_ids=selected_shared_parameter_ids,
            element_ids_list_is_inclusive_filter=True,
        )

        # update our status object
        return_value.update(purge_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print("{}\nFinished.".format(purge_status))

    return return_value
