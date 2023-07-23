"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to rename family files on a local or network drive.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This helper function expect a folder containing rename directive files. For format of those files refer to module RevitFamilyRenameFilesUtils

Note:

- The revit category is not used when renaming files but when renaming nested families.
- Any associated type catalogue files will also be renamed to match the new family name.
- Rename directives may not have the filePath property set if the directive is only meant to be used on loaded families.

"""


#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

# import clr
# import System
import os

from duHast.Revit.Family import family_rename_files_utils as rFamRenameUtils
from duHast.Utilities.Objects import result as res
from duHast.Utilities import files_io as fileIO


def _rename_files(rename_directives):
    """
    Renames family files and any associated catalogue files based on rename directives.

    :param rename_directives: List of tuples representing rename directives.
    :type rename_directives: [rename_directive]

    :return:
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value.update_sep(True, "Renaming families:")

    for rename_directive in rename_directives:
        try:
            # check if rename directive includes a file path ( might be empty if nested families only are to be renamed)
            if rename_directive.filePath != "":
                # attempt to rename family file
                try:
                    # build the new file name
                    new_full_name = os.path.join(
                        os.path.dirname(rename_directive.filePath),
                        rename_directive.newName + ".rfa",
                    )
                    if fileIO.file_exist(rename_directive.filePath):
                        os.rename(rename_directive.filePath, new_full_name)
                        return_value.append_message(
                            "{} -> {}".format(
                                rename_directive.name, rename_directive.newName
                            )
                        )
                    else:
                        return_value.update_sep(
                            False, "File not found: ".format(rename_directive.name)
                        )
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "Failed to rename file: {} with exception: {}".format(
                            rename_directive.name, e
                        ),
                    )

                # take care of catalogue files as well
                old_full_name = rename_directive.filePath[:-4] + ".txt"
                new_full_name = os.path.join(
                    os.path.dirname(rename_directive.filePath),
                    rename_directive.newName + ".txt",
                )
                oldname = rename_directive.name + ".txt"
                newname = rename_directive.newName + ".txt"
                try:
                    if fileIO.file_exist(old_full_name):
                        os.rename(old_full_name, new_full_name)
                        return_value.append_message("{} -> {}".format(oldname, newname))
                    else:
                        return_value.update_sep(
                            True, "No catalogue file found: {}".format(oldname)
                        )  # nothing gone wrong here...just no catalogue file present
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "Failed to rename file: {} with exception: {}".format(
                            old_full_name, e
                        ),
                    )
            else:
                return_value.update_sep(
                    True, "No file path found: {}".format(rename_directive.name)
                )  # nothing gone wrong here...just not required to rename a file
        except Exception as e:
            return_value.update_sep(
                False, "Failed to rename files with exception: ".format(e)
            )
    return return_value


def rename_family_files(directory_path):
    """
    Entry point for this module. Will read rename directives files in given directory and attempt to rename
    family files and any associated catalogue files accordingly.

    Note: Rename directive may not include a file path in situations where a loaded family only is to be renamed. This \
        will still return True in such a case.

    :param directory_path: Fully qualified directory path to where rename directive files are located.
    :type directory_path: str
    :return: 
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # get directives from folder
    rename_directives_result = rFamRenameUtils.get_rename_directives(directory_path)
    # check if anything came back
    if rename_directives_result.status:
        rename_directives = rename_directives_result.result
        # rename files as per directives
        return_value = _rename_files(rename_directives)
    else:
        return_value = rename_directives_result

    return return_value
