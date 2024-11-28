"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function around family types.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage import (
    FamilyTypeParameterDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)


def get_type_data_via_XML(doc, family_name, family_path, root_path, root_category_path):
    """
    Get the family type data from the family document using the XML extraction method.

    :param doc: The family document to extract the type data from.
    :type doc: rdb.Family
    :param family_name: The name of the family.
    :type family_name: str
    :param family_path: The path of the family file.
    :type family_path: str
    :param root_path: The root path of the family. (nesting tree of host family names)
    :type root_path: str
    :param root_category_path: The root category path of the family. (nesting tree of host family category names)
    :type root_category_path: str


    :return: A list of family type data objects.
    :rtype: list[FamilyTypeDataStorage]
    """

    # Set up list of type information to be returned
    type_data = []

    # this path is potentially empty if the document has not been saved...
    # not sure how revit wil react to that just yet
    path = doc.PathName

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
        temp_path_xml = temp_file.name

    try:
        # Save XML file to temporary location 
        # this is a method of the application object and does not require the family to be open...
        doc.Application.ExtractPartAtomFromFamilyFile(path, temp_path_xml)

        # Load XML file back in
        with open(temp_path_xml, "r") as file:
            xml_content = file.read()

        # Load the XML content
        doc_xml = XmlDocument()
        doc_xml.LoadXml(xml_content)

        # Add an XML namespace manager
        name_space_manager = XmlNamespaceManager(doc_xml.NameTable)
        name_space_manager.AddNamespace("atom", "http://www.w3.org/2005/Atom")
        name_space_manager.AddNamespace("A", "urn:schemas-autodesk-com:partatom")

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
                        parameter = FamilyTypeParameterDataStorage(
                            name=child_node.Name,
                            type=child_node.Attributes["type"].Value,
                            type_of_parameter=child_node.Attributes[
                                "typeOfParameter"
                            ].Value,
                            units=child_node.Attributes["units"].Value,
                            value=child_node.InnerText,
                        )
                        # Add type to family
                        parameters.append(parameter)

                # Set up a family type data storage object
                fam_type = FamilyTypeDataStorage(
                    root_name_path=root_path,
                    root_category_path=root_category_path,
                    family_name=family_name,
                    family_file_path=family_path,
                    family_type_name=family_type_name,
                    parameters=parameters,
                )

                # Add the family type to the list of types
                type_data.append(fam_type)

    finally:
        # Delete the temporary file
        if os.path.exists(temp_path_xml):
            os.remove(temp_path_xml)

    return type_data
