'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- date stamps (with varies formatting options)

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


#: default file stamp date format using underscores as delimiter: 21_03_01
import datetime
import os
from .files_io import get_file_name_without_ext


FILE_DATE_STAMP_YY_MM_DD = '%y_%m_%d'


#: file stamp date format using spaces as delimiter: 21 03 01
FILE_DATE_STAMP_YYMMDD_SPACE = '%y %m %d'


#: file stamp date format using spaces as delimiter: 2021 03 01
FILE_DATE_STAMP_YYYYMMDD_SPACE = '%Y %m %d'


#: file stamp date format using underscores as delimiter: 2021_03_01
FILE_DATE_STAMP_YYYY_MM_DD = '%Y_%m_%d'


#: file stamp date time format using underscores as delimiter: 2021_03_01_18_59_59
FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC = '%Y_%m_%d_%H_%M_%S'


#: time stamp using colons: 18:59:59
TIME_STAMP_HHMMSEC_COLON = '%H:%M:%S'


def get_file_date_stamp(format = FILE_DATE_STAMP_YY_MM_DD):
    '''
    Returns a date stamp formatted suitable for a file name.
    :param format: The date stamp format, defaults to FILE_DATE_STAMP_YY_MM_DD
    :type format: str, optional
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    '''

    d = datetime.datetime.now()
    return d.strftime(format)


#: folder date format: no delimiter 210301
FOLDER_DATE_STAMP_YYMMDD = '%y%m%d'


#: folder date format: no delimiter 20210301
FOLDER_DATE_STAMP_YYYYMMDD = '%Y%m%d'


#: folder date format: no delimiter 2021
FOLDER_DATE_STAMP_YYYY = '%Y'


def get_folder_date_stamp(format = FOLDER_DATE_STAMP_YYYYMMDD):
    '''
    Returns a date stamp formatted suitable for a folder name.
    :param format: The date stamp format, defaults to FOLDER_DATE_STAMP_YYYYMMDD
    :type format: str, optional
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    '''

    d = datetime.datetime.now()
    return d.strftime(format)


# get the date stamp in provided format
def get_date_stamp(format):
    '''
    Returns a date stamp formatted using past in format string.
    :param format: The date stamp format
    :type format: str
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    '''

    d = datetime.datetime.now()
    return d.strftime(format)


def get_date_stamped_file_name(file_path, file_extension = '.txt', file_suffix = ''):
    '''
    Returns a time stamped output file name based on the past in file name and file extension.
    :param file_path: Fully qualified file path to file
    :type file_path: str
    :param file_extension: File extension needs to include '.', defaults to '.txt'
    :type file_extension: str, optional
    :param file_suffix: File suffix will be appended after the name but before the file extension, defaults to ''
    :type file_suffix: str, optional
    :return: File name.
    :rtype: str
    '''

    # get date prefix for file name
    file_prefix = get_file_date_stamp()
    name = get_file_name_without_ext(file_path)
    return file_prefix + '_' + name + file_suffix + file_extension