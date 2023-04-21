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
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_tab import get_unique_headers


def combine_files(folder_path, file_prefix = '', file_suffix = '', file_extension='.txt', out_put_file_name = 'result.txt', file_getter = get_files_single_directory):
    '''
    Combines multiple text files into a single new file. Assumes same number of headers (columns) in each files.
    The new file will be saved into the same folder as the original files.
    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param out_put_file_name: The file name of the combined file, defaults to 'result.txt'
    :type out_put_file_name: str, optional
    :param file_getter: Function returning list of files to be combined, defaults to GetFilesSingleFolder
    :type file_getter: func(folder_path, file_prefix, file_suffix, file_extension), optional
    '''

    file_list = file_getter (folder_path, file_prefix, file_suffix, file_extension)
    with open(folder_path + '\\' + out_put_file_name, 'w' ) as result:
        file_counter = 0
        for file_ in file_list:
            line_counter = 0
            fp = open( file_, 'r' )
            lines = fp.readlines()
            fp.close()
            for line in lines:
                # ensure header from first file is copied over
                if(file_counter == 0 and line_counter == 0 or line_counter != 0):
                    result.write( line )
                line_counter += 1

            file_counter += 1

def append_to_file(source_file, append_file):
    '''
    Appends one text file to another. Assumes same number of headers (columns) in both files.
    :param source_file: The fully qualified file path of the file to which the other file will be appended.
    :type source_file: str
    :param append_file: The fully qualified file path of the file to be appended.
    :type append_file: str
    :return: If True file was appended without an exception, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        # read file to append into memory...hopefully will never get in GB range in terms of file size
        fp = codecs.open(append_file,'r',encoding='utf-8')
        lines=fp.readlines()
        fp.close()
        with codecs.open(source_file, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write( line )
    except Exception:
        flag = False
    return flag


def combine_files_header_independent(folder_path, file_prefix = '', file_suffix = '', file_extension='.txt', out_put_file_name = 'result.txt'):
    '''
    Used to combine report files into one file, files may have different number / named columns.
    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.
    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param out_put_file_name: The file name of the combined file, defaults to 'result.txt'
    :type out_put_file_name: str, optional
    '''

    file_list = glob.glob(folder_path + '\\' + file_prefix + '*' + file_suffix + file_extension)
    # build list of unique headers
    headers = get_unique_headers(file_list)
    # open output file
    with open(folder_path + '\\' + out_put_file_name, 'w' ) as result:
        file_counter = 0
        for file_ in file_list:
            line_counter = 0
            column_mapper = []
            for line in open( file_, 'r' ):
                line = line.rstrip('\n')
                # read the headers in file
                if (line_counter == 0):
                    headers_in_file = line.split('\t')
                    # replace any empty strings in header
                    file_name = get_file_name_without_ext(file_)
                    empty_header_counter = 0
                    for i in range(len(headers_in_file)):
                        # reformat any empty headers to be unique
                        if(headers_in_file[i] == ''):
                            headers_in_file[i] = file_name +  '.Empty.' + str(empty_header_counter)
                            empty_header_counter = empty_header_counter + 1
                    # match up unique headers with headers from this file
                    # build header mapping
                    for uh in headers:
                        if (uh in headers_in_file):
                            column_mapper.append(headers_in_file.index(uh))
                        else:
                            column_mapper.append(-1)
                # ensure unique header is written
                if(file_counter == 0 and line_counter == 0):
                    headers.append('\n')
                    result.write('\t'.join(headers))
                elif(line_counter != 0):
                    # write out padded rows
                    row_data = line.split('\t')
                    #print(row_data)
                    padded_row = []
                    for cm in column_mapper:
                        if(cm == -1):
                            # this column does not exist in this file
                            padded_row.append('N/A')
                        elif (cm > len(row_data)):
                            # less columns in file than mapper index (should'nt happen??)
                            padded_row.append('index out of bounds')
                        else:
                            padded_row.append(row_data[cm])
                    padded_row.append('\n')
                    result.write('\t'.join(padded_row))
                line_counter += 1
            file_counter += 1