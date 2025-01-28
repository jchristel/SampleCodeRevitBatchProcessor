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
from duHast.Revit.Family.family_rename_files_utils import _read_rename_directives
from duHast.Revit.Family.Data.family_rename_loaded_families import (
    _rename_loaded_families,
)
from duHast.Revit.Family import family_utils as rFamUtils
from duHast.pyRevit.file_picker import get_file_path_from_user
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict


def rename_loaded_families(doc, output, forms):
    """
    Renames loaded families based on a csv file.
    Refer to duHast.Revit.Family.family_rename_files_utils for csv file format.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if files where renamed without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get the user to select the file to be imported
    file_path = get_file_path_from_user(
        forms=forms, title="Select rename file", file_extension="csv"
    )
    if file_path is None:
        print("No file selected. Exiting.")
        return_value.update_sep(False, "No file selected. Exiting.")
        return return_value

    # attempt to read rename file
    print("Reading file: {}".format(file_path))
    data = []
    try:
        data = _read_rename_directives([file_path])
    except Exception as e:
        message = "failed to read rename file with exception: {}".format(e)
        print(message)
        return_value.update_sep(False, message=message)
        return return_value

    # check if any data in file
    if len(data) == 0:
        message = "Rename file did not contain any data"
        return_value.update_sep(False, message=message)
        return return_value

    # get all family in file
    families = get_name_and_category_to_family_dict(doc)

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Renaming families: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # rename them
        rename_status = _rename_loaded_families(
            doc=doc,
            rename_directives=data,
            families=families,
            progress_callback=progress_callback,
        )

        # update our status object
        return_value.update(rename_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(rename_status.message)

    print("Finished.")

    return return_value
