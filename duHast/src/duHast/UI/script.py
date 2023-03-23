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
from duHast.UI import FileItem as fi
# import file list methods
from duHast.UI import FileList as fl
# import UI class
import UIFileSelect as UIFs
# import settings class
from duHast.UI import FileSelectSettings as set
# import workloader utils
from duHast.UI import Workloader as wl

# import bim360 utils from Library
from duHast.APISamples import UtilBIM360 as ub360

def main(argv):
    '''
    Entry point.

    :param argv: A list of string representing arguments past in.
    :type argv: [str]
    '''

    # get arguments
    gotArgs, settings = processArgs(argv)
    if(gotArgs):
        # retrieve revit file data
        revitFiles = GetFileData(settings)
        # check whether this is a BIM360 project or file system and assign
        # data retriever method accordingly
        if(isBIM360File(revitFiles)):
            getData = fl.BucketToTaskListBIM360
        else:
            getData = fl.BucketToTaskListFileSystem
        # check if anything came back
        if(len(revitFiles) > 0):
            # lets show the window
            ui = UIFs.MyWindow(xamlFullFileName_, revitFiles, settings)
            uiResult = ui.ShowDialog()
            if(uiResult):
                # build bucket list
                buckets = wl.DistributeWorkload(settings.outputFileNum, ui.selectedFiles, fl.getFileSize)
                # write out file lists
                counter = 0
                for bucket in buckets:
                    fileName =  os.path.join(settings.outputDir, 'Tasklist_' + str(counter)+ '.txt')
                    statusWrite = fl.writeRevitTaskFile(fileName, bucket, getData)
                    print (statusWrite.message)
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

def processArgs(argv):
    '''
    Processes past in arguments and checks whether inputs are valid.

    :param argv: List of arguments
    :type argv: _type_

    :return: 
        - True if arguments past in are valid, otherwise False.
        - FIle select settings object instance.
    :rtype: bool, :class:`.FileSelectionSettings`
    '''

    inputDirFile = ''
    outputDirectory = ''
    outputFileNumber = 1
    revitFileExtension = '.rvt'
    includeSubDirsInSearch = False
    gotArgs = False
    try:
        opts, args = getopt.getopt(argv,"hsi:o:n:e:",["subDir","input=","outputDir=",'numberFiles=','fileExtension='])
    except getopt.GetoptError:
        print ('test.py -s -i <input> -o <outputDirectory> -n <numberOfOutputFiles> -e <fileExtension>')
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <input> -o <outputDirectory> -n <numberOfOutputFiles> -e <fileExtension>')
        elif opt in ("-s", "--subDir"):
            includeSubDirsInSearch = True
        elif opt in ("-i", "--input"):
            inputDirFile = arg
            gotArgs = True
        elif opt in ("-o", "--outputDir"):
            outputDirectory = arg
            gotArgs = True
        elif opt in ("-n", "--numberFiles"):
            try:
                value = int(arg)
                outputFileNumber = value
                gotArgs = True
            except ValueError:
                print (arg + ' value is not an integer')
                gotArgs = False
        elif opt in ("-e", "--fileExtension"):
            revitFileExtension = arg
            gotArgs = True

    # check if input values are valid
    if (outputFileNumber < 0 or outputFileNumber > 100):
        gotArgs = False
        print ('The number of output files must be bigger then 0 and smaller then 100')
    if(not FileExist(inputDirFile)):
        gotArgs = False
        print ('Invalid input directory or file path: ' + str(inputDirFile))
    if(not FileExist(outputDirectory)):
        gotArgs = False
        print ('Invalid output directory: ' + str(outputDirectory))
    if(revitFileExtension != '.rvt' and revitFileExtension != '.rfa'):
        gotArgs = False
        print ('Invalid file extension: [' + str(revitFileExtension) + '] expecting: .rvt or .rfa')

    return gotArgs, set.FileSelectionSettings(inputDirFile, includeSubDirsInSearch, outputDirectory, outputFileNumber, revitFileExtension)

def GetFolderPathFromFile(filePath):
    '''
    Returns the directory from a fully qualified file path.

    :param filePath: A fully qualified file path.
    :type filePath: str

    :return: A fully qualified directory path. 
        On exception an empty string.
    :rtype: str
    '''

    try:
        value = os.path.dirname(filePath)
    except Exception:
        value = ''
    return value

def FileExist(path):
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


def GetFileData(settings):
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

    revitFiles = []
    # check whether input is a directory path or a text file (csv) containing BIM 360 data
    # since we tested for a valid path initially it will need to be either one...
    try:
        if(os.path.isfile(settings.inputDir)):
            # got a text file...extract BIM 360 data
            revitFiles = ub360.GetBIM360Data(settings.inputDir)
        elif(os.path.isdir(settings.inputDir)):
            # check a to search for files is to include sub dirs
            revitFilesUnfiltered = []
            if(settings.inclSubDirs):
                # get revit files in input dir and subdirs
                revitFilesUnfiltered = fl.getRevitFilesInclSubDirs(settings.inputDir, settings.revitFileExtension)
            else:
                # get revit files in input dir
                revitFilesUnfiltered = fl.getRevitFiles(settings.inputDir, settings.revitFileExtension)
            # check for max path violations!
            # The specified path, file name, or both are too long. The fully qualified file name must be less than 260 characters, and the directory name must be less than 248 characters.
            for revitFile in revitFilesUnfiltered:
                # remove any back up files from selection
                if(fl.isBackUpFile(os.path.basename(revitFile.name)) == False):
                    if(len(os.path.dirname(os.path.abspath(revitFile.name))) < 248  and len(revitFile.name) < 260 ):
                        revitFiles.append(revitFile)
                    else:
                        print ('Max path length violation: ' + revitFile.name)
                        print ('File has been removed from selection!')
    except Exception as e:
        print ('An exception occurred during BIM360 file read! ' + str(e))
        # return an empty list which will cause this script to abort
        revitFiles = []
    return revitFiles

def isBIM360File(revitFiles):
    '''
    Checks whether the first item in a file item list belongs to a BIM 360 project.

    Checks whether Project GUID property on file item object is None.

    :param revitFiles: List of file items.
    :type revitFiles: [:class:`.FileItem`]
    :return: True if BIM360 file, otherwise False.
    :rtype: bool
    '''
    BIM360File = False
    for r in revitFiles:
        if(r.BIM360ProjectGUID != None):
            BIM360File = True
            break
    return BIM360File

#: the directory this script lives in
currentScriptDir_ = os.path.dirname(__file__) #GetFolderPathFromFile(sys.path[0])

#: xaml file name of file select UI
xamlFile_ = 'ui.xaml'

#: xaml full path
xamlFullFileName_ =  os.path.join(currentScriptDir_, xamlFile_)

#: module entry
if __name__ == "__main__":
   main(sys.argv[1:])