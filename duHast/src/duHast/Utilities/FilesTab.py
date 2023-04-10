'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to tab separated text files. 
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
import csv
from duHast.Utilities.Utility import GetFirstRowInFile
from duHast.Utilities.FilesIO import GetFileNameWithoutExt


def GetUniqueHeaders(files):
    '''
    Gets a list of alphabetically sorted headers retrieved from text files.
    Assumes:
    - first row in each file is the header row
    - headers are separated by <tab> character
    :param files: List of file path from which the headers are to be returned.
    :type files: list of str
    :return: List of headers.
    :rtype: list of str
    '''

    headersInAllFiles = {}
    for f in files:
        data = GetFirstRowInFile(f)
        if (data is not None):
            rowSplit = data.split('\t')
            headersInAllFiles[GetFileNameWithoutExt(f)] = rowSplit
    headersUnique = []
    for headerByFile in headersInAllFiles:
        emptyHeaderCounter = 0
        for header in headersInAllFiles[headerByFile]:
            # reformat any empty headers to be unique
            if(header == ''):
                header = headerByFile +  '.Empty.' + str(emptyHeaderCounter)
                emptyHeaderCounter = emptyHeaderCounter + 1
            if(header not in headersUnique):
                headersUnique.append(header)
    return sorted(headersUnique)


def writeReportData(fileName, header, data, writeType = 'w'):
    '''
    Function writing out report information.
    :param fileName: The reports fully qualified file path.
    :type fileName: str
    :param header: list of column headers
    :type header: list of str
    :param data: list of list of strings representing row data
    :type data: [[str,str,..]]
    :param writeType: Flag indicating whether existing report file is to be overwritten 'w' or appended to 'a', defaults to 'w'
    :type writeType: str, optional
    '''

    with codecs.open(fileName, writeType, encoding='utf-8') as f:
        # check if header is required
        if(len(header) > 0):
            f.write('\t'.join(header + ['\n']))
        # check if data is required
        if(len(data) > 0):
            for d in data:
                if (len(d) > 1):
                    f.write('\t'.join(d + ['\n']))
                elif(len(d) == 1):
                    f.write(d[0] + '\n')
        f.close()


def ReadTabSeparatedFile(filePath, increaseMaxFieldSizeLimit = False):
    '''
    Read a tab separated text file into a list of rows, where each row is another list.
    :param filePath: The fully qualified file path to the tab separated text file.
    :type filePath: str
    :return:  A list of list of strings representing the data in each row.
    :rtype: list of list of str
    '''

    rowList = []

    # hard coded hack
    if(increaseMaxFieldSizeLimit):
        csv.field_size_limit(2147483647)

    try:
        with open (filePath) as f:
            reader = csv.reader(f, dialect='excel-tab')
            for row in reader: # each row is a list
                rowList.append(row)
            f.close()
    except Exception as e:
        print (filePath, str(e))
        rowList = []
    return rowList