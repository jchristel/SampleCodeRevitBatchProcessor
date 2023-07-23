"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a custom helper functions for marker files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- bim 360 folder
- export file name
- copy export files
- read the current file list in docFile objects

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# import settings
import settings as settings  # sets up all commonly used variables and path locations!

# import from library
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_csv import write_report_data_as_csv
import docFile as df

# import from library
from duHast.Utilities.files_csv import read_csv_file

# --------------- write file -------------------

# writes out the document data file back in the script folder
# with updated revision information retrieved from marker files
def write_new_file_data(doc_files, marker_file_data):
    """
    _summary_

    :param doc_files: _description_
    :type doc_files: _type_
    :param marker_file_data: _description_
    :type marker_file_data: _type_
    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    flag = False
    # compare lists
    doc_files_sorted = []
    for cfd in doc_files:
        match = False
        for nfd in marker_file_data:
            print("new: {} vs old: {}".format(nfd, cfd))
            if (
                nfd.existing_file_name == cfd.existing_file_name
                and nfd.file_extension == cfd.file_extension
            ):
                match = True
                doc_files_sorted.append(nfd)
                break
        if match == False:
            doc_files_sorted.append(cfd)
    data = convert_class_to_string(doc_files_sorted)
    flag = write_new_data(settings.REVISION_DATA_FILEPATH, data)
    return_value.update(flag)
    return_value.result.append(doc_files_sorted)
    return return_value


# write new revision data out to file
def write_new_data(path, data):
    """
    _summary_

    :param path: _description_
    :type path: _type_
    :param data: _description_
    :type data: _type_
    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    try:
        write_report_data_as_csv(path, [], data)
        return_value.append_message("Wrote new meta data file to: {}".format(path))
    except Exception as e:
        return_value.update_sep(False,"Failed to write data file: {} with exception: {}".format(path, e))
    return return_value


def convert_class_to_string(doc_files):
    """
    _summary_

    :param doc_files: _description_
    :type doc_files: _type_
    :return: _description_
    :rtype: _type_
    """
    
    data = []
    for doc_file in doc_files:
        data.append(doc_file.get_data())
    return data


def read_current_file(revision_data_path):
    """
    Read the current revision data file list located in script location.

    :param revision_data_path: fully qualified file path to revision data file
    :type revision_data_path: str
    :return: a list containing current file data
    :rtype: [docFile]
    """

    reference_list = []
    try:
        rows = read_csv_file(revision_data_path)
        for row in rows:
            reference_list.append(df.docFile(row))
    except Exception as e:
        print(str(e))
        reference_list = []
    return reference_list