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

import os

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.Family.family_rename_files_utils import (
    _read_rename_directives,
)
from duHast.Revit.Family.Data.Objects.family_directive_rename import (
    FamilyDirectiveRename,
)
from duHast.Utilities.files_get import (
    get_files_from_directory_walker_with_filters_simple,
)
from duHast.Revit.Family.family_rename_files import _rename_files
from duHast.pyRevit.file_picker import get_file_path_from_user


def find_files(file_paths, file_name):
    """
    Finds files with a specific name in a list of file paths.

    :param file_paths: A list of file paths.
    :type file_paths: list[str]
    :param file_name: The file name to search for.
    :type file_name: str

    :return: A list of file paths that match the file name.
    :rtype: list[str]
    """

    return [path for path in file_paths if os.path.basename(path) == file_name]


def updated_rename_directives(directory, rename_directives):
    """
    Updates the rename directives with a file path of a matching family in directory.

    Mote:

    - if multiple matches or no matches are found, the user is informed via print statements.

    :param directory: The directory to search for families.
    :type directory: str
    :param rename_directives: The rename directives.
    :type rename_directives: list[FamilyRenameDirective]

    :return: A list of updated rename directives.
    :rtype: list[FamilyRenameDirective
    """

    new_directives = []
    # the below assumes rename directives contain a fully qualified file path...
    # get all families in the chosen directory and it sub dirs:
    families_in_directory = get_files_from_directory_walker_with_filters_simple(
        folder_path=directory, file_extension=".rfa"
    )

    # update the collection with values from the revit model
    for family in rename_directives:
        # check the match status!!
        files_matching = find_files(families_in_directory, family.name + ".rfa")
        if len(files_matching) == 1:
            data = FamilyDirectiveRename(
                family.name,
                family.category,
                files_matching[0],
                family.new_name,
            )
            new_directives.append(data)
        elif len(files_matching) == 0:
            print("No match found for family: {}".format(family.name))
        else:
            print(
                "Multiple matches found for {}: \n{}".format(
                    family.name, files_matching
                )
            )
    return new_directives


def rename_families_in_folder(doc, output, forms):
    """
    Renames families in a directory based on a csv file.
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

    file_path = get_file_path_from_user(
        forms=forms, title="Select rename file", file_extension="csv"
    )
    if file_path is None:
        print("No file selected. Exiting.")
        return_value.update_sep(False, "No file selected. Exiting.")
        return return_value

    # attempt to read rename file
    print("Reading file: {}".format(file_path))
    rename_directives = []
    try:
        rename_directives = _read_rename_directives([file_path])
    except Exception as e:
        message = "failed to read rename file with exception: {}".format(e)
        print(message)
        return_value.update_sep(False, message=message)
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Renaming families in directory: {value} of {max_value}", cancellable=True
    ) as pb:
        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # rename them
        rename_status = _rename_files(rename_directives, progress_callback)

        # update our status object
        return_value.update(rename_status)

        # check for cancel
        if pb.cancelled:
            return_value.update_sep(False, "User cancelled.")

    print(rename_status.message)

    print("Finished.")

    return return_value
