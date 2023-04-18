'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to combining text files. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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


import codecs
import glob
from duHast.Utilities.FilesIO import get_file_name_without_ext
from duHast.Utilities.FilesGet import get_files_single_directory
from duHast.Utilities.FilesTab import get_unique_headers


def combine_files(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt', fileGetter = get_files_single_directory):
    '''
    Combines multiple text files into a single new file. Assumes same number of headers (columns) in each files.
    The new file will be saved into the same folder as the original files.
    :param folderPath: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :param outPutFileName: The file name of the combined file, defaults to 'result.txt'
    :type outPutFileName: str, optional
    :param fileGetter: Function returning list of files to be combined, defaults to GetFilesSingleFolder
    :type fileGetter: func(folderPath, filePrefix, fileSuffix, fileExtension), optional
    '''

    file_list = fileGetter (folderPath, filePrefix, fileSuffix, fileExtension)
    with open(folderPath + '\\' + outPutFileName, 'w' ) as result:
        fileCounter = 0
        for file_ in file_list:
            lineCounter = 0
            fp = open( file_, 'r' )
            lines = fp.readlines()
            fp.close()
            for line in lines:
                # ensure header from first file is copied over
                if(fileCounter == 0 and lineCounter == 0 or lineCounter != 0):
                    result.write( line )
                lineCounter += 1

            fileCounter += 1

def append_to_file(sourceFile, appendFile):
    '''
    Appends one text file to another. Assumes same number of headers (columns) in both files.
    :param sourceFile: The fully qualified file path of the file to which the other file will be appended.
    :type sourceFile: str
    :param appendFile: The fully qualified file path of the file to be appended.
    :type appendFile: str
    :return: If True file was appended without an exception, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        # read file to append into memory...hopefully will never get in GB range in terms of file size
        fp = codecs.open(appendFile,'r',encoding='utf-8')
        lines=fp.readlines()
        fp.close()
        with codecs.open(sourceFile, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write( line )
    except Exception:
        flag = False
    return flag


def combine_files_header_independent(folderPath, filePrefix = '', fileSuffix = '', fileExtension='.txt', outPutFileName = 'result.txt'):
    '''
    Used to combine report files into one file, files may have different number / named columns.
    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.
    :param folderPath: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :param outPutFileName: The file name of the combined file, defaults to 'result.txt'
    :type outPutFileName: str, optional
    '''

    file_list = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    # build list of unique headers
    headers = get_unique_headers(file_list)
    # open output file
    with open(folderPath + '\\' + outPutFileName, 'w' ) as result:
        fileCounter = 0
        for file_ in file_list:
            lineCounter = 0
            columnMapper = []
            for line in open( file_, 'r' ):
                line = line.rstrip('\n')
                # read the headers in file
                if (lineCounter == 0):
                    headersInFile = line.split('\t')
                    # replace any empty strings in header
                    fileName = get_file_name_without_ext(file_)
                    emptyHeaderCounter = 0
                    for i in range(len(headersInFile)):
                        # reformat any empty headers to be unique
                        if(headersInFile[i] == ''):
                            headersInFile[i] = fileName +  '.Empty.' + str(emptyHeaderCounter)
                            emptyHeaderCounter = emptyHeaderCounter + 1
                    # match up unique headers with headers from this file
                    # build header mapping
                    for uh in headers:
                        if (uh in headersInFile):
                            columnMapper.append(headersInFile.index(uh))
                        else:
                            columnMapper.append(-1)
                # ensure unique header is written
                if(fileCounter == 0 and lineCounter == 0):
                    headers.append('\n')
                    result.write('\t'.join(headers))
                elif(lineCounter != 0):
                    # write out padded rows
                    rowData = line.split('\t')
                    #print(rowData)
                    paddedRow = []
                    for cm in columnMapper:
                        if(cm == -1):
                            # this column does not exist in this file
                            paddedRow.append('N/A')
                        elif (cm > len(rowData)):
                            # less columns in file than mapper index (should'nt happen??)
                            paddedRow.append('index out of bounds')
                        else:
                            paddedRow.append(rowData[cm])
                    paddedRow.append('\n')
                    result.write('\t'.join(paddedRow))
                lineCounter += 1
            fileCounter += 1