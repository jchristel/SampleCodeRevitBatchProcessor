"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to Solibri IFC optimizer.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List of imports:

- :class:`.Result`
- :module: Utility

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


import subprocess
from System.IO import Path

from duHast.Utilities.Objects import result as res
from duHast.Utilities import files_get as fileGet, files_io as fileIO


#: The default install path for solibri ifc optimizer.
solibri_install_path_ = (
    r"C:\Program Files\Solibri\IFCOptimizer\Solibri IFC Optimizer.exe"
)


def optimize_all_ifc_files_in_directory(directory_path):
    """
    Function applying third party IFC optimizer to all ifc files in a given folder.

    Original files will be deleted.

    :param directory_path: The directory path where IFC files are located
    :type directory_path: str
    :return:
        Result class instance.

        - Optimizer status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path(s) of the optimized file(s).

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain generic exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check if ifc optimizer is installed:
    if fileIO.file_exist(solibri_install_path_):
        return_value.message = "Solibri IFC optimizer is installed."
        ifc_files = fileGet.get_files(directory_path, ".ifc")
        if len(ifc_files) > 0:
            process_files_result = process_ifc_files(ifc_files, directory_path)
            return_value.update(process_files_result)
        else:
            return_value.append_message(
                "No IFC files found in directory: {}".format(directory_path)
            )
    else:
        return_value.update_sep(
            False, "No IFC optimizer installed at: {}".format(solibri_install_path_)
        )
    return return_value


def optimize_ifc_files_in_list(ifc_files, directory_path):
    """
    This function will optimize all IFC files in a given list of fully qualified file path to ifc files.

    Will check whether Solibri IFC optimizer is installed.

    :param ifc_files: List containing fully qualified file path of ifc files to be optimized.
    :type ifc_files: list of str
    :param directory_path: Directory of where the optimized IFC file(s) are to be saved.
    :type directory_path: str

    :return:
        Result class instance.

        - Optimizer status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path(s) of the optimized file(s).

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain generic exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check if ifc optimizer is installed:
    if fileIO.file_exist(solibri_install_path_):
        return_value.message = "Solibri IFC optimizer is installed."
        if len(ifc_files) > 0:
            process_files_result = process_ifc_files(ifc_files, directory_path)
            return_value.update(process_files_result)
        else:
            return_value.append_message("IFC file list is empty.")
    else:
        return_value.update_sep(
            False, "No IFC optimizer installed at: " + str(solibri_install_path_)
        )
    return return_value


def process_ifc_files(ifc_files, directory_path):
    """
    This function will optimize all IFC files in a given list of fully qualified file path to ifc files.

    Will not check whether Solibri IFC optimizer is installed.

    :param ifc_files: List containing fully qualified file path of ifc files to be optimized.
    :type ifc_files: list of str
    :param directory_path: Directory of where the optimized IFC file(s) are to be saved.
    :type directory_path: str

    :return:
        Result class instance.

        - Optimizer status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path(s) of the optimized file(s).

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain generic exception message.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    files_to_delete = []
    files_to_rename = []
    if len(ifc_files) > 0:
        return_value.append_message("found ifc files: {}".format(len(ifc_files)))
        for ifc_file in ifc_files:
            s = subprocess.check_call(
                [
                    r"C:\Program Files\Solibri\IFCOptimizer\Solibri IFC Optimizer.exe",
                    "-in=" + ifc_file,
                    "-out=" + directory_path,
                    "-ifc",
                    "-force",
                ]
            )
            # check what came back
            if s == 0:
                # all went ok:
                return_value.append_message("Optimized file: {}".format(ifc_file))
                files_to_delete.append(ifc_file)  # full file path
                # get the rename information
                # contains old and new file name
                rename = []
                p = fileIO.get_directory_path_from_file_path(ifc_file)
                if p != "":
                    new_file_path = (
                        str(p)
                        + "\\"
                        + str(Path.GetFileNameWithoutExtension(ifc_file))
                        + "_optimized.ifc"
                    )
                    rename.append(new_file_path)
                    rename.append(ifc_file)
                    files_to_rename.append(rename)
            else:
                # something went wrong
                return_value.update_sep(
                    False, "Failed to optimize file: {}".format(ifc_file)
                )
        # clean up
        for file_to_delete in files_to_delete:
            status_delete = fileIO.file_delete(file_to_delete)
            if status_delete:
                return_value.append_message(
                    "Deleted original file: {}".format(file_to_delete)
                )
            else:
                return_value.update_sep(
                    False, "Failed to delete original file: {}".format(file_to_delete)
                )
        for file_to_rename in files_to_rename:
            status_rename = fileIO.rename_file(file_to_rename[0], file_to_rename[1])
            if status_rename:
                return_value.append_message(
                    "Renamed original file: {} to: {}".format(
                        file_to_rename[0], file_to_rename[1]
                    )
                )
            else:
                return_value.update_sep(
                    False,
                    "Failed to rename original file: {}".format(file_to_rename[0]),
                )
    else:
        return_value.append_message("No IFC files found at: {}".format(directory_path))
    return return_value
