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
from System.Xml import XmlDocument, XmlNamespaceManager

import tempfile
import os

from Autodesk.Revit.DB import Element

from duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage import (
    FamilyTypeParameterDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_file_name_without_ext, get_directory_path_from_file_path


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


def read_xml_into_storage(doc_xml, family_name, family_path):
    """
    Read the XML data into the storage object.

    :param doc_xml: The XML document.
    :type doc_xml: XmlDocument
    :param family_name: The name of the family.
    :type family_name: str
    :param family_path: The path of the family file.
    :type family_path: str

    :return: A list of family type data objects.
    :rtype: list[FamilyTypeDataStorage]
    """

    type_data = []
    # Add an XML namespace manager
    name_space_manager = XmlNamespaceManager(doc_xml.NameTable)
    name_space_manager.AddNamespace("atom", "http://www.w3.org/2005/Atom")
    name_space_manager.AddNamespace("A", "urn:schemas-autodesk-com:partatom")

    # get some family information i.e. the root category path
    root_category_path = "None"

    # Select the family node
    family_node = doc_xml.SelectSingleNode("//A:family", name_space_manager)

    # Get the family parameters
    for part_node in family_node.SelectNodes("A:part", name_space_manager):
        # Get the family type name
        family_type_name = None
        for child_node in part_node.ChildNodes:
            if child_node.Name == "title":
                family_type_name = child_node.InnerText
                break

        # If we got a type name, add the parameters, their values and units, parameter type and type of parameter
        if family_type_name:
            parameters = []
            for child_node in part_node.ChildNodes:
                if child_node.Name != "title":
                    
                    # attempt to read out values
                    name = "unknown type"
                    try:
                        name = child_node.Name
                    except Exception as e:
                        name ="{}: {}".format(name, e)
                    
                    type = "unknown type"
                    try:
                        type = child_node.Attributes["type"].Value
                    except Exception as e:
                        type ="{}: {}".format(type, e)
                    
                    type_of_parameter = "unknown type"
                    try:
                        type_of_parameter = child_node.Attributes["typeOfParameter"].Value
                    except Exception as e:
                        type_of_parameter ="{}: {}".format(type_of_parameter, e)
                    
                    units = "unknown type"
                    try:
                        units = child_node.Attributes["units"].Value
                    except Exception as e:
                        units ="{}: {}".format(units, e)

                    # Create a parameter object
                    parameter = FamilyTypeParameterDataStorage(
                        name=name,
                        type=type,
                        type_of_parameter=type_of_parameter,
                        units=units,
                        value=child_node.InnerText,
                    )
                    
                    # Add type to family
                    parameters.append(parameter)

            # Set up a family type data storage object
            fam_type = FamilyTypeDataStorage(
                root_name_path=family_name,
                root_category_path=root_category_path,
                family_name=family_name,
                family_file_path=family_path,
                family_type_name=family_type_name,
                parameters=parameters,
            )

            # Add the family type to the list of types
            type_data.append(fam_type)
    return type_data


def get_type_data_via_XML_from_family_file(application, family_name, family_path, use_temporary_file=True):
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
        else:
            dir_out = get_directory_path_from_file_path(family_path)
            family_name = get_file_name_without_ext(family_path)

            # Write the data to an XML file and read it back
            doc_xml = write_data_to_xml_file_and_read_it_back(action, os.path.join(dir_out,family_name + ".xml"))

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
