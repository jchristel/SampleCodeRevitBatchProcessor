"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit file operations utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


import Autodesk.Revit.DB as rdb

from duHast.Utilities import files_io as fileIO
from duHast.Utilities.Objects import result as res


def sync_file(
    doc, compact_central_file=False  # type: bool
):
    # type: (...) -> res.Result
    """
    Synchronizes a Revit central file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param compact_central_file: option to compact the central file, defaults to False
    :type compact_central_file: bool, optional
    :return:
        Result class instance.
        - .result = True if successfully synced file. Otherwise False.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # set up sync settings
    ro = rdb.RelinquishOptions(True)
    transaction_options = rdb.TransactWithCentralOptions()
    sync = rdb.SynchronizeWithCentralOptions()
    sync.Comment = "Synchronized by Revit Batch Processor"
    sync.Compact = compact_central_file
    sync.SetRelinquishOptions(ro)
    # Synch it
    try:
        # save local first ( this seems to prevent intermittent crash on sync(?))
        doc.Save()
        doc.SynchronizeWithCentral(transaction_options, sync)
        # relinquish all
        rdb.WorksharingUtils.RelinquishOwnership(doc, ro, transaction_options)
        return_value.message = "Successfully synched file."
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: {}".format(e))
    return return_value


def saves_as_workshared_file(
    doc, full_file_name  # type: str
):
    # type: (...) -> res.Result
    """
    Saves a Revit project file as a workshared file.
    Save as options are:
    Workset configuration is : Ask users on open to specify.
    Any existing file will be overwritten.
    Number of backups is 5
    File will bew compacted on save.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param full_file_name: The fully qualified file path of where to save the file.
    :type full_file_name: string
    :return:
        Result class instance.
        - .result = True if successfully saved file, otherwise False.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        worksharing_save_as_option = rdb.WorksharingSaveAsOptions()
        worksharing_save_as_option.OpenWorksetsDefault = (
            rdb.SimpleWorksetConfiguration.AskUserToSpecify
        )
        worksharing_save_as_option.SaveAsCentral = True
        save_option = rdb.SaveAsOptions()
        save_option.OverwriteExistingFile = True
        save_option.SetWorksharingOptions(worksharing_save_as_option)
        save_option.MaximumBackups = 5
        save_option.Compact = True
        doc.SaveAs(full_file_name, save_option)
        return_value.message = "Successfully saved file: " + str(full_file_name)
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: {}".format(e))
    return return_value


def save_as_family(
    doc,
    target_directory_path,
    current_full_file_name,
    name_data,
    file_extension=".rfa",
    compact_file=False,
):

    """
    Saves a family file under new name in given location.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param target_directory_path: The directory path of where to save the file.
    :type target_directory_path: str
    :param current_full_file_name: The current (old) name of the file.
    :type current_full_file_name: str
    :param name_data:  Old name and new name are Revit file names without file extension. Used to rename the family on save from old name to new name.
    :type name_data: List of string arrays in format[[oldname, newName]]
    :param file_extension: The file extension used for the new file, defaults to '.rfa'
    :type file_extension: str, optional
    :param compact_file: Flag whether family is to be compacted on save, defaults to False
    :type compact_file: bool, optional
    :return:
        Result class instance.
            - .result = True if successfully saved file, otherwise False.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    revit_file_name = fileIO.get_file_name_without_ext(current_full_file_name)
    new_file_name = ""
    match = False
    # find new file name in list past in
    for old_name, new_name in name_data:
        if revit_file_name.startswith(old_name):
            match = True
            return_value.message = "Found file name match for: {} new name: {}".format(
                revit_file_name, new_name
            )
            # save file under new name
            new_file_name = target_directory_path + "\\" + new_name + file_extension
            break
    if match == False:
        # save under same file name
        new_file_name = target_directory_path + "\\" + revit_file_name + file_extension
        return_value.message = "Found no file name match for: {}".format(
            current_full_file_name
        )
    try:
        # setup save as option
        so = rdb.SaveAsOptions()
        so.OverwriteExistingFile = True
        so.MaximumBackups = 5
        so.SetWorksharingOptions(None)
        so.Compact = compact_file
        doc.SaveAs(new_file_name, so)
        return_value.update_sep(True, "Saved file: {}".format(new_file_name))
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to save revit file to new location with exception: {}".format(e),
        )
    return return_value


def save_as(
    doc, target_directory_path, current_full_file_name, name_data, file_extension=".rvt"
):

    """
    Saves a project file under new name in given location.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param target_directory_path: The directory path of where to save the file.
    :type target_directory_path: str
    :param current_full_file_name: The current (old) name of the file.
    :type current_full_file_name: str
    :param name_data: Old name and new name are revit file names without file extension. Used to rename the model on save from old name to new name.
    :type name_data: List of string arrays in format[[oldname, newName]]
    :param file_extension: The file extension used for the new file, defaults to '.rvt'
    :type file_extension: str, optional
    :return:
        Result class instance.
        - .result = True if successfully saved file, otherwise False.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # added str() around this expression to satisfy sphinx auto code documentation
    # it will throw an exception when concatenating the string in the return statement
    revit_file_name = str(fileIO.get_file_name_without_ext(current_full_file_name))
    new_file_name = ""
    match = False
    for old_name, new_name in name_data:
        if revit_file_name.startswith(old_name):
            match = True
            return_value.message = "Found file name match for: {} new name: {}".format(
                revit_file_name, new_name
            )
            # save file under new name
            new_file_name = target_directory_path + "\\" + new_name + file_extension
            break
    if match == False:
        # save under same file name
        new_file_name = target_directory_path + "\\" + revit_file_name + file_extension
        # added str.format around this expression to satisfy sphinx auto code documentation
        return_value.message = "Found no file name match for: {}".format(
            current_full_file_name
        )
    try:
        return_value.status = saves_as_workshared_file(doc, new_file_name).status
        return_value.append_message("Saved file: {}".format(new_file_name))
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to save revit file to new location; {} with exception: ".format(
                new_file_name, e
            ),
        )
    return return_value


def save_file(
    doc, compact_file=False  # type: bool
):
    # type: (...) -> res.Result
    """
    Saves a non workshared Revit file. To be used for families and non workshared revit files only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param compact_file: True file will be compacted on save, defaults to False
    :type compact_file: bool, optional
    :return:
            Result class instance.
            - .result = True if file was saved successfully. Otherwise False.
            - .message = 'Saved revit file!'
            On exception:
            - result.status (bool) will be False.
            - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        save_options = rdb.SaveOptions()
        save_options.Compact = compact_file
        doc.Save(save_options)
        return_value.update_sep(True, "Saved revit file!")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to save revit file with exception: {}".format(e)
        )
    return return_value


def enable_worksharing(
    doc,  #
    workset_name_grid_level="Shared Levels and Grids",  # type: str
    workset_name="Workset1",  # type: str
):
    # type: (...) -> res.Result
    """
    Enables worksharing in a non workshared revit project file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param workset_name_grid_level: _description_, defaults to 'Shared Levels and Grids'
    :type workset_name_grid_level: str, optional
    :param workset_name: _description_, defaults to 'Workset1'
    :type workset_name: str, optional

    :return:
            Result class instance.
            - .result = True if worksharing was enabled successfully. Otherwise False.
            - .message = 'Successfully enabled worksharing.'
            On exception:
            - result.status (bool) will be False.
            - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        doc.EnableWorksharing(workset_name_grid_level, workset_name)
        return_value.message = "Successfully enabled worksharing."
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: {}".format(e))
    return return_value
