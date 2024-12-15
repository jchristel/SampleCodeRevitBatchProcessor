"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function to read xml family type data into storage objects.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Separate module for ease of testing and maintainability.
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
import datetime
import re

clr.AddReference("System.Xml")
from System.Xml import XmlDocument, XmlNamespaceManager

from duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage import (
    FamilyTypeParameterDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)
from duHast.Utilities.Objects.result import Result


def read_xml_file(file_path):
    """
    Read xml data from a file into a XmlDocument object.

    :param file_path: The path to the file.
    :type file_path: str

    :return: The data read back from the XML file.
    :rtype: XmlDocument or None if an error occurred.
    """

    doc_xml = None

    try:
        # Read the data back from the file
        # added utf-8 encoding to deal with special characters (i.e. °)
        with open(file_path, "r", encoding="utf-8") as file:
            xml_content = file.read()

        # Load the XML content
        doc_xml = XmlDocument()
        doc_xml.LoadXml(xml_content)

    except Exception as e:
        pass

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

    # Get the category nodes ( there will be more than one)
    for cat_node in doc_xml.SelectNodes("//atom:category", name_space_manager):
        dummy_term = ""
        dummy_scheme = ""

        for child_node in cat_node.ChildNodes:
            if child_node.Name == "term":
                dummy_term = child_node.InnerText
            if child_node.Name == "scheme":
                dummy_scheme = child_node.InnerText
        # check if this is the category name
        if dummy_scheme == "adsk:revit:grouping":
            root_category_path = dummy_term

     # get the date and time of the last update
    last_updated_date = None
    last_updated_time = None

    # Select the <updated> node directly under the <entry> node
    updated_node = doc_xml.SelectSingleNode("//atom:updated", name_space_manager)
    if updated_node is not None:
        last_updated_datetime = updated_node.InnerText
        
        # Convert the date-time string to a date and time
        try:
            dt = datetime.datetime.strptime(last_updated_datetime, "%Y-%m-%dT%H:%M:%SZ")
            last_updated_date = dt.date().isoformat()  # Convert to date-only string
            last_updated_time = dt.time().isoformat()  # Convert to time-only string
        except ValueError as e:
            print("Error parsing date-time: {}".format(e))
    else:
        print("updated_node not found")

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
                    name = "unknown name"
                    try:
                        name = child_node.Name
                    except Exception as e:
                        name = "{}".format(name, e)

                    type = "unknown type"
                    try:
                        type = child_node.Attributes["type"].Value
                    except Exception as e:
                        type = "{}".format(type, e)

                    type_of_parameter = "unknown type of parameter"
                    try:
                        type_of_parameter = child_node.Attributes[
                            "typeOfParameter"
                        ].Value
                    except Exception as e:
                        type_of_parameter = "{}".format(type_of_parameter, e)

                    # there are parameters without units (i.e. text parameters)
                    units = "unitless"
                    try:
                        units = child_node.Attributes["units"].Value
                    except Exception as e:
                        pass

                    # attempt to read out values
                    p_value = "unknown value"
                    try:
                        p_value = child_node.InnerText
                    except Exception as e:
                        pass

                    # Check if p_value contains a number followed by a unit string (including special characters like °)
                    number_unit_pattern = re.compile(r"^(\d+(\.\d+)?)\s*([^\d\s]+)$")
                    match = number_unit_pattern.match(p_value)
                    if match:
                        # found a unit string, just return the number
                        p_value = match.group(1)
                    else:
                        # No unit string found, just use the value as is
                        pass
                    
                    # Create a parameter object
                    parameter = FamilyTypeParameterDataStorage(
                        name=name,
                        type=type,
                        type_of_parameter=type_of_parameter,
                        units=units,
                        value=p_value,
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
                last_updated_date=last_updated_date,
                last_updated_time=last_updated_time,
            )

            # Add the family type to the list of types
            type_data.append(fam_type)
    return type_data
