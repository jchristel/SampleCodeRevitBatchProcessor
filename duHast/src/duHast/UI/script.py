'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The entry point for the file selection GUI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

import sys, getopt, os


# import file item class
from duHast.UI import file_item as fi
# import file list methods
from duHast.UI import file_list as fl
# import UI class
import UIFileSelect as UIFs
# import settings class
from duHast.UI import file_select_settings as set
# import workloader utils
from duHast.UI import workloader as wl

# import bim360 utils from Library
from duHast.Revit.BIM360 import util_bim_360 as ub360

def main(argv):
    '''
    Entry point.

    :param argv: A list of string representing arguments past in.
    :type argv: [str]
    '''

    # get arguments
    got_args, settings = process_args(argv)
    if(got_args):
        # retrieve revit file data
        revit_files = get_file_data(settings)
        # check whether this is a BIM360 project or file system and assign
        # data retriever method accordingly
        if(is_bim_360_file(revit_files)):
            get_data = fl.bucket_to_task_list_bim_360
        else:
            get_data = fl.bucket_to_task_list_file_system
        # check if anything came back
        if(len(revit_files) > 0):
            # lets show the window
            ui = UIFs.MyWindow(XAML_FULL_FILE_NAME, revit_files, settings)
            ui_result = ui.ShowDialog()
            if(ui_result):
                # build bucket list
                buckets = wl.distribute_workload(settings.output_file_num, ui.selectedFiles, fl.get_file_size)
                # write out file lists
                counter = 0
                for bucket in buckets:
                    file_name =  os.path.join(settings.output_dir, 'Tasklist_' + str(counter)+ '.txt')
                    status_write = fl.write_revit_task_file(file_name, bucket, get_data)
                    print (status_write.message)
                    counter += 1
                print('Finished writing out task files')
                sys.exit(0)
            else:
                # do nothing...
                print ('No files selected!')
                sys.exit(2)
        else:
            # show message box
            print ('No files found!')
            sys.exit(2)
    else:
        # invalid or no args provided... get out
        sys.exit(1)

def process_args(argv):
    '''
    Processes past in arguments and checks whether inputs are valid.

    :param argv: List of arguments
    :type argv: _type_

    :return: 
        - True if arguments past in are valid, otherwise False.
        - FIle select settings object instance.
    :rtype: bool, :class:`.FileSelectionSettings`
    '''

    input_dir_file = ''
    output_directory = ''
    output_file_number = 1
    revit_file_extension = '.rvt'
    include_sub_dirs_in_search = False
    got_args = False
    try:
        opts, args = getopt.getopt(argv,"hsi:o:n:e:",["subDir","input=","outputDir=",'numberFiles=','fileExtension='])
    except getopt.GetoptError:
        print ('test.py -s -i <input> -o <output_directory> -n <numberOfOutputFiles> -e <fileExtension>')
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <input> -o <output_directory> -n <numberOfOutputFiles> -e <fileExtension>')
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
                print (arg + ' value is not an integer')
                got_args = False
        elif opt in ("-e", "--fileExtension"):
            revit_file_extension = arg
            got_args = True

    # check if input values are valid
    if (output_file_number < 0 or output_file_number > 100):
        got_args = False
        print ('The number of output files must be bigger then 0 and smaller then 100')
    if(not file_exist(input_dir_file)):
        got_args = False
        print ('Invalid input directory or file path: ' + str(input_dir_file))
    if(not file_exist(output_directory)):
        got_args = False
        print ('Invalid output directory: ' + str(output_directory))
    if(revit_file_extension != '.rvt' and revit_file_extension != '.rfa'):
        got_args = False
        print ('Invalid file extension: [' + str(revit_file_extension) + '] expecting: .rvt or .rfa')

    return got_args, set.FileSelectionSettings(input_dir_file, include_sub_dirs_in_search, output_directory, output_file_number, revit_file_extension)

def get_directory_from_file_path(file_path):
    '''
    Returns the directory from a fully qualified file path.

    :param file_path: A fully qualified file path.
    :type file_path: str

    :return: A fully qualified directory path. 
        On exception an empty string.
    :rtype: str
    '''

    try:
        value = os.path.dirname(file_path)
    except Exception:
        value = ''
    return value

def file_exist(path):
    '''
    Checks whether a file exists.

    :param path: A fully qualified file path.
    :type path: str

    :return: True if file exists, otherwise False.
    :rtype: bool
    '''

    try:
        value = os.path.exists(path)
    except Exception:
        value = False
    return value


def get_file_data(settings):
    '''
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
    '''

    revit_files = []
    # check whether input is a directory path or a text file (csv) containing BIM 360 data
    # since we tested for a valid path initially it will need to be either one...
    try:
        if(os.path.isfile(settings.inputDir)):
            # got a text file...extract BIM 360 data
            revit_files = ub360.get_bim_360_file_data(settings.inputDir)
        elif(os.path.isdir(settings.inputDir)):
            # check a to search for files is to include sub dirs
            revit_files_unfiltered = []
            if(settings.inclSubDirs):
                # get revit files in input dir and subdirs
                revit_files_unfiltered = fl.get_revit_files_incl_sub_dirs(settings.inputDir, settings.revitFileExtension)
            else:
                # get revit files in input dir
                revit_files_unfiltered = fl.get_revit_files(settings.inputDir, settings.revitFileExtension)
            # check for max path violations!
            # The specified path, file name, or both are too long. The fully qualified file name must be less than 260 characters, and the directory name must be less than 248 characters.
            for revit_file in revit_files_unfiltered:
                # remove any back up files from selection
                if(fl.is_back_up_file(os.path.basename(revit_file.name)) == False):
                    if(len(os.path.dirname(os.path.abspath(revit_file.name))) < 248  and len(revit_file.name) < 260 ):
                        revit_files.append(revit_file)
                    else:
                        print ('Max path length violation: ' + revit_file.name)
                        print ('File has been removed from selection!')
    except Exception as e:
        print ('An exception occurred during BIM360 file read! ' + str(e))
        # return an empty list which will cause this script to abort
        revit_files = []
    return revit_files

def is_bim_360_file(revit_files):
    '''
    Checks whether the first item in a file item list belongs to a BIM 360 project.

    Checks whether Project GUID property on file item object is None.

    :param revit_files: List of file items.
    :type revit_files: [:class:`.FileItem`]
    :return: True if BIM360 file, otherwise False.
    :rtype: bool
    '''
    bim360_file = False
    for r in revit_files:
        if(r.BIM360ProjectGUID != None):
            bim360_file = True
            break
    return bim360_file

#: the directory this script lives in
CURRENT_SCRIPT_DIRECTORY = os.path.dirname(__file__) #GetFolderPathFromFile(sys.path[0])

#: xaml file name of file select UI
XAML_FILE = 'ui.xaml'

#: xaml full path
XAML_FULL_FILE_NAME =  os.path.join(CURRENT_SCRIPT_DIRECTORY, XAML_FILE)

#: module entry
if __name__ == "__main__":
   main(sys.argv[1:])