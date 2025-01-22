"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to xml files. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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


import clr
clr.AddReference("System.Xml")
from System.Xml import XmlDocument

from duHast.Utilities.files_base_read import read_non_column_based_text_file
from duHast.Utilities.Objects.result import Result
from duHast.UI.file_list import get_revit_files


def read_xml_file(file_path):
    """
    Reads an XML file and returns the content as a string.
    :param file_path: The path to the XML file.

    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will the XML Document instance.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """
    
    return_value = Result()

    read_result = read_non_column_based_text_file(file_path)
    return_value.update(read_result)

    if read_result.status is False:
        return return_value
    
    try:
        # Load the XML content
        doc_xml = XmlDocument()
        doc_xml.LoadXml(read_result.result)
        return_value.result = doc_xml

    except Exception as e:
        return_value.update_sep(False, "Error while reading the XML file: {}" .format(e))
    
    return return_value


def get_xml_files_from_directory(directory):
    """
    Gets all XML files from a directory.
    :param directory: The directory to search for XML files.
    :type directory: str

    :return: A list of XML files.
    :rtype: [:class:`.FileItem`]
    """

    xml_files = []
    try:
        xml_files = get_revit_files(directory, "*.xml")
    except Exception:
        pass
    return xml_files


def get_all_xml_files_from_directories(process_directories):
    """
    Get all xml files from the directories

    :param process_directories: list of directories to search for xml files
    :type process_directories: list
    
    :return: list of xml files found
    :rtype: [:class:`FileItem`]
    """

    files_found = []
    try:
        # get all xml files from the directory
        for directory in process_directories:
            files = get_xml_files_from_directory(directory)
            files_found = files_found + files
    except Exception as e:
        raise Exception("Failed to gather xml files with exception: {}".format(e))
    return files_found