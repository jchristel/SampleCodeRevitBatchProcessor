"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function around family types data extraction using Revit xml export functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supports 2 methods of data extraction:

- from family file on disk
- from family element instance in document

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import tempfile
import os

from Autodesk.Revit.DB import Element

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import (
    get_file_name_without_ext,
    get_directory_path_from_file_path,
)
from duHast.Revit.Family.Utility.xml_family_type_reader import read_xml_into_storage


def write_data_to_temp_xml_file_and_read_it_back(an_action_to_write_xml_data):
    """
    Write the data to a temp XML file and read it back.

    :param an_action_to_write_xml_data: The action to write the XML data.
    :type an_action_to_write_xml_data: function

    :return: The data read back from the XML file.
    :rtype: XmlDocument or None if an error occurred.
    """

    doc_xml = None

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
        temp_path_xml = temp_file.name

    try:

        # Write the data to the file
        an_action_to_write_xml_data(temp_path_xml)

        # Read the data back from the file
        with open(temp_path_xml, "r") as file:
            xml_content = file.read()

        # Load the XML content
        doc_xml = XmlDocument()
        doc_xml.LoadXml(xml_content)

    finally:
        # Delete the temporary file
        if os.path.exists(temp_path_xml):
            os.remove(temp_path_xml)

    return doc_xml


def write_data_to_xml_file_and_read_it_back(an_action_to_write_xml_data, xml_file_path):
    """
    Write the data to an XML file and read it back.

    :param an_action_to_write_xml_data: The action to write the XML data.
    :type an_action_to_write_xml_data: function
    :param xml_file_path: The path of the XML file.
    :type xml_file_path: str

    :return: The data read back from the XML file.
    :rtype: XmlDocument or None if an error occurred.
    """

    doc_xml = None

    try:

        # Write the data to the file
        an_action_to_write_xml_data(xml_file_path)

        # Read the data back from the file
        with open(xml_file_path, "r") as file:
            xml_content = file.read()

        # Load the XML content
        doc_xml = XmlDocument()
        doc_xml.LoadXml(xml_content)
    except Exception as e:
        return None
    return doc_xml


def get_type_data_via_XML_from_family_file(
    application, family_name, family_path, use_temporary_file=True
):
    """
    Get the family type data from the family document using the XML extraction method.
    This can be used to extract the type data from a family document within a Revit session but without opening the family in Revit.

    :param application: The Revit application object.
    :type application: Autodesk.Revit.ApplicationServices.Application
    :param family_name: The name of the family.
    :type family_name: str
    :param family_path: The path of the family file.
    :type family_path: str
    :param use_temporary_file: Whether to use a temporary file for the XML data.
    :type use_temporary_file: bool

    :return: A result object with .result containing a list of family type data objects. (or empty if failed)
    :rtype: Result
    """

    return_value = Result()

    # Set up list of type information to be returned
    type_data = []

    try:
        # set up action to write xml data
        def action(temp_path_xml):
            # Save XML file to temporary location
            # this is a method of the application object and does not require the family to be open...
            application.ExtractPartAtomFromFamilyFile(family_path, temp_path_xml)

        doc_xml = None

        if use_temporary_file:
            # Write the data to an XML file and read it back
            doc_xml = write_data_to_temp_xml_file_and_read_it_back(action)
            return_value.append_message("Writing XML data to temp file.")
        else:
            dir_out = get_directory_path_from_file_path(family_path)
            family_name = get_file_name_without_ext(family_path)
            return_value.append_message(
                "Writing XML data to file: {}".format(
                    os.path.join(dir_out, family_name + ".xml")
                )
            )
            # Write the data to an XML file and read it back
            doc_xml = write_data_to_xml_file_and_read_it_back(
                action, os.path.join(dir_out, family_name + ".xml")
            )

        # check if an xml document was created
        if doc_xml is None:
            return_value.update_sep(False, "No XML document was created.")
            return return_value

        # read the xml data into the storage object
        type_data = read_xml_into_storage(doc_xml, family_name, family_path)

        # store list in return object
        return_value.result.append(type_data)
    except Exception as e:
        return_value.update_sep(False, "{}".format(e))

    return return_value


def get_type_data_via_XML_from_family_object(revit_family):
    """
    Get the family type data from the family element in a REvit document using the XML extraction method.

    :param revit_family: The Revit family object.
    :type revit_family: Autodesk.Revit.DB.Family

    :return: A result object with .result containing a list of family type data objects. (or empty if failed)
    :rtype: Result
    """

    return_value = Result()
    # Set up list of type information to be returned
    type_data = []

    try:
        # set up action to write xml data
        def action(temp_path_xml):
            # Save XML file to temporary location
            revit_family.ExtractPartAtom(temp_path_xml)

        # Write the data to an XML file and read it back
        doc_xml = write_data_to_temp_xml_file_and_read_it_back(action)

        # check if an xml document was created
        if doc_xml is None:
            return_value.update_sep(False, "No XML document was created.")
            return return_value

        # read the xml data into the storage object
        type_data = read_xml_into_storage(
            doc_xml, family_name=Element.Name.GetValue(revit_family), family_path=""
        )

        # store list in return object
        return_value.result.append(type_data)
    except Exception as e:
        return_value.update_sep(False, "{}".format(e))

    return return_value
