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
from duHast.Utilities.files_io import get_first_row_in_file
from duHast.Utilities.files_io import get_file_name_without_ext


def get_unique_headers(files):
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

    headers_in_all_files = {}
    for f in files:
        data = get_first_row_in_file(f)
        if (data is not None):
            row_split = data.split('\t')
            headers_in_all_files[get_file_name_without_ext(f)] = row_split
    headers_unique = []
    for header_by_file in headers_in_all_files:
        empty_header_counter = 0
        for header in headers_in_all_files[header_by_file]:
            # reformat any empty headers to be unique
            if(header == ''):
                header = header_by_file +  '.Empty.' + str(empty_header_counter)
                empty_header_counter = empty_header_counter + 1
            if(header not in headers_unique):
                headers_unique.append(header)
    return sorted(headers_unique)


def write_report_data(file_name, header, data, write_type = 'w'):
    '''
    Function writing out report information.

    :param file_name: The reports fully qualified file path.
    :type file_name: str
    :param header: list of column headers
    :type header: list of str
    :param data: list of list of strings representing row data
    :type data: [[str,str,..]]
    :param write_type: Flag indicating whether existing report file is to be overwritten 'w' or appended to 'a', defaults to 'w'
    :type write_type: str, optional
    '''

    with codecs.open(file_name, write_type, encoding='utf-8') as f:
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


def read_tab_separated_file(file_path, increase_max_field_size_limit = False):
    '''
    Read a tab separated text file into a list of rows, where each row is another list.
    :param file_path: The fully qualified file path to the tab separated text file.
    :type file_path: str
    :return:  A list of list of strings representing the data in each row.
    :rtype: list of list of str
    '''

    row_list = []

    # hard coded hack
    if(increase_max_field_size_limit):
        csv.field_size_limit(2147483647)

    try:
        with open (file_path) as f:
            reader = csv.reader(f, dialect='excel-tab')
            for row in reader: # each row is a list
                row_list.append(row)
            f.close()
    except Exception as e:
        print (file_path, str(e))
        row_list = []
    return row_list