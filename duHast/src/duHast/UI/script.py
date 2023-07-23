"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The entry point for the file selection GUI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import sys, getopt, os

# to get to the root folder of this repo
sys.path.append(
    os.path.join(os.path.realpath(__file__), os.pardir, os.pardir, os.pardir)
)

# import file item class
# from duHast.UI import file_item as fi
# import file list methods
from duHast.UI import file_list as fl

# import UI class
from duHast.UI import ui_file_select as UIFs

# import settings class
from duHast.UI import file_select_settings as set

# import workloader utils
from duHast.UI import workloader as wl

from duHast.Utilities.files_csv import read_csv_file, get_first_row_in_csv_file
from duHast.Utilities.files_tab import get_first_row_in_file_no_strip
from duHast.Utilities.files_io import file_exist, get_file_size, FILE_SIZE_IN_KB
from duHast.UI.file_item import MyFileItem

# import bim360 utils from Library
from duHast.Revit.BIM360 import util_bim_360 as ub360


def main(argv):
    """
    Entry point.

    :param argv: A list of string representing arguments past in.
    :type argv: [str]
    """

    # get arguments
    got_args, settings = process_args(argv)
    if got_args:
        # retrieve revit file data
        revit_files = get_file_data(settings)
        # check whether this is a BIM360 project or file system and assign
        # data retriever method accordingly
        if is_bim_360_file(revit_files):
            get_data = fl.bucket_to_task_list_bim_360
        else:
            get_data = fl.bucket_to_task_list_file_system
        # check if anything came back
        if len(revit_files) > 0:
            # lets show the window
            ui = UIFs.MyWindow(XAML_FULL_FILE_NAME, revit_files, settings)
            ui_result = ui.ShowDialog()
            if ui_result:
                # build bucket list
                buckets = wl.distribute_workload(
                    settings.output_file_num, ui.selectedFiles, fl.get_file_size
                )
                # write out file lists
                counter = 0
                for bucket in buckets:
                    file_name = os.path.join(
                        settings.output_dir, "Tasklist_" + str(counter) + ".txt"
                    )
                    status_write = fl.write_revit_task_file(file_name, bucket, get_data)
                    print(status_write.message)
                    counter += 1
                print("Finished writing out task files")
                sys.exit(0)
            else:
                # do nothing...
                print("No files selected!")
                sys.exit(2)
        else:
            # show message box
            print("No files found!")
            sys.exit(2)
    else:
        # invalid or no args provided... get out
        sys.exit(1)


def process_args(argv):
    """
    Processes past in arguments and checks whether inputs are valid.

    :param argv: List of arguments
    :type argv: _type_

    :return:
        - True if arguments past in are valid, otherwise False.
        - FIle select settings object instance.
    :rtype: bool, :class:`.FileSelectionSettings`
    """

    input_dir_file = ""
    output_directory = ""
    output_file_number = 1
    revit_file_extension = ".rvt"
    include_sub_dirs_in_search = False
    got_args = False
    try:
        opts, args = getopt.getopt(
            argv,
            "hsi:o:n:e:",
            ["subDir", "input=", "outputDir=", "numberFiles=", "fileExtension="],
        )
    except getopt.GetoptError:
        print(
            "test.py -s -i <input> -o <output_directory> -n <numberOfOutputFiles> -e <fileExtension>"
        )
    for opt, arg in opts:
        if opt == "-h":
            print(
                "test.py -i <input> -o <output_directory> -n <numberOfOutputFiles> -e <fileExtension>"
            )
        elif opt in ("-s", "--subDir"):
            include_sub_dirs_in_search = True
        elif opt in ("-i", "--input"):
            input_dir_file = arg
            got_args = True
        elif opt in ("-o", "--outputDir"):
            output_directory = arg
            got_args = True
        elif opt in ("-n", "--numberFiles"):
            try:
                value = int(arg)
                output_file_number = value
                got_args = True
            except ValueError:
                print(arg + " value is not an integer")
                got_args = False
        elif opt in ("-e", "--fileExtension"):
            revit_file_extension = arg
            got_args = True

    # check if input values are valid
    if output_file_number < 0 or output_file_number > 100:
        got_args = False
        print("The number of output files must be bigger then 0 and smaller then 100")
    if not file_exist(input_dir_file):
        got_args = False
        print("Invalid input directory or file path: " + str(input_dir_file))
    if not file_exist(output_directory):
        got_args = False
        print("Invalid output directory: " + str(output_directory))
    if revit_file_extension != ".rvt" and revit_file_extension != ".rfa":
        got_args = False
        print(
            "Invalid file extension: ["
            + str(revit_file_extension)
            + "] expecting: .rvt or .rfa"
        )

    return got_args, set.FileSelectionSettings(
        input_dir_file,
        include_sub_dirs_in_search,
        output_directory,
        output_file_number,
        revit_file_extension,
    )


def get_directory_from_file_path(file_path):
    """
    Returns the directory from a fully qualified file path.

    :param file_path: A fully qualified file path.
    :type file_path: str

    :return: A fully qualified directory path.
        On exception an empty string.
    :rtype: str
    """

    try:
        value = os.path.dirname(file_path)
    except Exception:
        value = ""
    return value


def get_file_data(settings):
    """
    Retrieves Revit file data from either:

        - directory on a file server

        - a text file containing BIM 360 project data
            - text file needs to be a .csv
            - format:
                - 0 Revit Version:YYYY,Project GUID, File GUID, file size, BIM 360 file path

    :param settings: A file select settings object instance.
    :type settings: :class:`.FileSelectionSettings`

    :return: List of file items
    :rtype: [:class:`.FileItem`]
    """

    revit_files = []
    # check whether input is a directory path or a text file (csv) containing BIM 360 data
    # since we tested for a valid path initially it will need to be either one...
    try:
        if os.path.isfile(settings.input_directory):
            # got a text file...extract BIM 360 data
            revit_files = get_file_data_from_text_file(settings.input_directory)
        elif os.path.isdir(settings.input_directory):
            # check a to search for files is to include sub dirs
            revit_files_unfiltered = []
            if settings.incl_sub_dirs:
                # get revit files in input dir and subdirs
                revit_files_unfiltered = fl.get_revit_files_incl_sub_dirs(
                    settings.input_directory, settings.revit_file_extension
                )
            else:
                # get revit files in input dir
                revit_files_unfiltered = fl.get_revit_files(
                    settings.input_directory, settings.revit_file_extension
                )
            # check for max path violations!
            # The specified path, file name, or both are too long. The fully qualified file name must be less than 260 characters, and the directory name must be less than 248 characters.
            for revit_file in revit_files_unfiltered:
                # remove any back up files from selection
                if fl.is_back_up_file(os.path.basename(revit_file.name)) == False:
                    if (
                        len(os.path.dirname(os.path.abspath(revit_file.name))) < 248
                        and len(revit_file.name) < 260
                    ):
                        revit_files.append(revit_file)
                    else:
                        print("Max path length violation: {}".format(revit_file.name))
                        print("File has been removed from selection!")
    except Exception as e:
        print("An exception occurred during BIM360 file read! {}".format(e))
        # return an empty list which will cause this script to abort
        revit_files = []
    return revit_files


def get_files_from_list_file(file_path_csv):
    """
    Reads server based file data, the fully qualified file path, from a task file list file in csv format.

    :param filePathCSV: The fully qualified file path to the task list file.
    :type filePathCSV: str

    :return: A list of MyFileItem objects. If an exception occurred an empty list will be returned.
    :rtype: :class:`.MyFileItem`
    """

    revit_files = []
    try:
        # read the CSV into rows
        rows = read_csv_file(file_path_csv)
        # check whether anything came back
        if len(rows) > 0:
            # process rows
            for rowData in rows:
                if len(rowData) > 0:
                    file_size = get_file_size(rowData[0], FILE_SIZE_IN_KB)
                    dummy = MyFileItem(rowData[0], file_size)
                    revit_files.append(dummy)
    except Exception as e:
        print("An exception occurred during row processing! " + str(e))
        # return an empty list which will cause this script to abort
        revit_files = []
    return revit_files


def get_file_data_from_text_file(file_path):
    """
    Reads a file server based task list file. This file can either be a BIM360 task list file or \
        a task list file containing file server based file path in a single column.

    :param filePath: The fully qualified file path to the task list file.
    :type filePath: str
    :return: A list of MyFileItem objects.
    :rtype: :class:`.MyFileItem`
    """

    files = []
    # if file is empty an empty list will be returned
    # also need to check whether this is a csv file...
    if file_path.lower().endswith(".csv"):
        # list of entries in first row
        row = get_first_row_in_csv_file(file_path)
    else:
        row = get_first_row_in_file_no_strip(file_path)
        # make sure we get a list of entries
        if row is not None:
            row = row.split("\t")
    if row is not None:
        # bim 360 or autodesk construction cloud files have at least 3 entries
        if len(row) > 2:
            files = ub360.get_bim_360_file_data(file_path)
        else:
            files = get_files_from_list_file(file_path)
    return files


def is_bim_360_file(revit_files):
    """
    Checks whether the first item in a file item list belongs to a BIM 360 project.

    Checks whether Project GUID property on file item object is None.

    :param revit_files: List of file items.
    :type revit_files: [:class:`.FileItem`]
    :return: True if BIM360 file, otherwise False.
    :rtype: bool
    """

    bim_360_file = False
    for revit_file in revit_files:
        if revit_file.bim_360_project_guid != None:
            bim_360_file = True
            break
    return bim_360_file


#: the directory this script lives in
CURRENT_SCRIPT_DIRECTORY = os.path.dirname(
    __file__
)  # GetFolderPathFromFile(sys.path[0])

#: xaml file name of file select UI
XAML_FILE = "ui.xaml"

#: xaml full path
XAML_FULL_FILE_NAME = os.path.join(CURRENT_SCRIPT_DIRECTORY, XAML_FILE)

#: module entry
if __name__ == "__main__":
    main(sys.argv[1:])
