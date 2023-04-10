'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to comma separated text files. 
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


def ReadCSVfile(filepathCSV, increaseMaxFieldSizeLimit = False):
    '''
    Read a csv file into a list of rows, where each row is another list.
    :param filepathCSV: The fully qualified file path to the csv file.
    :type filepathCSV: str
    :return: A list of list of strings representing the data in each row.
    :rtype: list of list of str
    '''

    rowList = []

    # hard coded hack
    if(increaseMaxFieldSizeLimit):
        csv.field_size_limit(2147483647)

    try:
        with open(filepathCSV) as csvFile:
            reader = csv.reader(csvFile)
            for row in reader: # each row is a list
                rowList.append(row)
    except Exception as e:
        print (str(e))
        rowList = []
    return rowList


def GetFirstRowInCSVFile(filePath):
    '''
    Reads the first line of a csv text file and returns it as a list of strings
    :param filePath: The fully qualified file path.
    :type filePath: str
    :return: The first row of a text file.
    :rtype: str
    '''

    row = []
    try:
        with open(filePath) as f:
            reader = csv.reader(f)
            row = f.readline()
            row = row.strip()
    except Exception:
        row = []
    return row


def writeReportDataAsCSV (fileName, header, data, writeType = 'w'):
    '''
    Function writing out report information as CSV file.
    :param fileName: The reports fully qualified file path.
    :type fileName: str
    :param header: list of column headers
    :type header: list of str
    :param data: list of list of strings representing row data
    :type data: [[str,str,..]]
    :param writeType: Flag indicating whether existing report file is to be overwritten 'w' or appended to 'a', defaults to 'w'
    :type writeType: str, optional
    '''

    # open the file in the write mode
    with codecs.open(fileName, writeType, encoding='utf-8') as f:
        # create the csv writer
        writer = csv.writer(f)
        # check header
        if(len(header) > 0):
            writer.writerow(header)
        if(len(data) > 0):
            for d in data:
                # write a row to the csv file
                writer.writerow(d)
        f.close()