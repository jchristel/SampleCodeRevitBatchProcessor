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
from System.Xml import XmlNamespaceManager, XmlDocument

from duHast.Revit.Family.Data.Objects.family_type_parameter_data_storage import (
    FamilyTypeParameterDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)
from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import (
    FamilyTypeDataStorageManager,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)
from duHast.Utilities.utility import encode_ascii

from duHast.Utilities.string_operations import (
    remove_currency_sign,
    replace_new_lines,
    remove_trailing_characters_from_number_string,
)

# Constants
# place holder for unitless parameters
UNITLESS = "unitless"
NAME_UNKNOWN = "unknown name"
TYPE_UNKNOWN = "unknown type" # type of parameter is unknown (options are custom, shared, system)
VALUE_UNKNOWN = "unknown value"
PARAMETER_STORAGE_TYPE_UNKNOWN = "unknown storage type"
FAMILY_TYPE_NAME_UNKNOWN = "unknown family type name"


# XML node attribute names translation of parameter properties
# the parameter name
PARAMETER_NAME = "Parameter Name"
# the parameter type (options are custom, shared, system)
PARAMETER_INTERNAL_TYPE = "Parameter Internal Type"
# the storage type of a parameter (string, yes /no,etc)
PARAMETER_STORAGE_TYPE = "Parameter Storage Type"
# the units of a parameter
PARAMETER_UNITS = "Parameter Units"

# XML node name mapper of properties for parameters
# the translated properties of a parameter and the xml attribute name
PARAMETER_NODE_PROPERTIES = {
    PARAMETER_NAME: "name",
    PARAMETER_INTERNAL_TYPE:"type",
    PARAMETER_STORAGE_TYPE: "typeOfParameter",
    PARAMETER_UNITS: "units",
}

def get_parameter(xml_node, family_name, root_category_path, family_path, family_type_name = FAMILY_TYPE_NAME_UNKNOWN, default_value=VALUE_UNKNOWN):
    """
    Get a parameter from the XML node.

    :param xml_node: The XML node.
    :type xml_node: XmlNode
    :param family_name: The name of the family.
    :type family_name: str
    :param root_category_path: The root category path.
    :type root_category_path: str
    :param family_path: The path of the family file.
    :type family_path: str
    :param family_type_name: The name of the family type.
    :type family_type_name: str
    :param default_value: The default value to use if the parameter value is not set.
    :type default_value: str

    :return: A family type parameter data storage object.
    :rtype: :class:`.FamilyTypeParameterDataStorage`
    """

    try:
        # attempt to read out values
        name = NAME_UNKNOWN
        try:
            name = xml_node.Name
        except Exception as e:
            name = "{}".format(name, e)

        type = TYPE_UNKNOWN
        try:
            type = xml_node.Attributes[PARAMETER_NODE_PROPERTIES[PARAMETER_INTERNAL_TYPE]].Value
        except Exception as e:
            type = "{}".format(type, e)

        type_of_parameter = PARAMETER_STORAGE_TYPE_UNKNOWN
        try:
            type_of_parameter = xml_node.Attributes[PARAMETER_NODE_PROPERTIES[PARAMETER_STORAGE_TYPE]].Value
        except Exception as e:
            type_of_parameter = "{}".format(type_of_parameter, e)

        # there are parameters without units (i.e. text parameters)
        units = UNITLESS
        try:
            units = xml_node.Attributes[PARAMETER_NODE_PROPERTIES[PARAMETER_UNITS]].Value
        except Exception as e:
            pass

        # set the parameter value to the default value
        p_value = default_value

        # attempt to read out values if required
        if p_value == VALUE_UNKNOWN:
        
            try:
                # replace any new row characters with space and remove trailing spaces
                p_value = replace_new_lines(xml_node.InnerText)
            except Exception as e:
                pass

            # check if the value is a number and contains thousands separators
            if (
                type_of_parameter
                in FamilyTypeParameterDataStorage.unit_type_compare_values_as_floats
            ):
                # remove any thousands separators
                p_value = p_value.replace(",", "")
                # remove any currency signs
                p_value = remove_currency_sign(p_value)
                # remove any trailing units
                p_value = remove_trailing_characters_from_number_string(p_value)
        else:
            # go with the default value
            pass

        # family_name can either be just the family name or the family root path
        # check which one it is:
        root_name_path = family_name
        family_name_checked = family_name

        # split the file name at nesting separator
        family_name_split = family_name.split(NESTING_SEPARATOR)
        
        # check if the family name contains a nesting separator
        if len(family_name_split) > 0:
            # yes, so the fam name path is the last part
            family_name_checked = family_name_split[-1]

        # Create a parameter object 
        # make sure all values are encoded to ascii to avoid 
        # issues with special characters when writing to file
        parameter = FamilyTypeParameterDataStorage(
            root_name_path = encode_ascii(root_name_path),
            root_category_path = encode_ascii(root_category_path),
            family_name = encode_ascii(family_name_checked),
            family_type_name=encode_ascii(family_type_name),
            family_file_path=encode_ascii(family_path),
            name=encode_ascii(name),
            type=encode_ascii(type),
            type_of_parameter=encode_ascii(type_of_parameter),
            units=encode_ascii(units),
            value=encode_ascii(p_value),
        )

        return parameter
    except Exception:

        return None



def get_unique_parameters_from_family_xml(doc_xml, family_name, root_category_path, family_path):
    """
    Get all unique parameters from the family type XML document by inspecting every part node representing a family type.
    
    Note:
    The part atom export will only contain parameters for a family type if they have a value set.

    :param doc_xml: The XML document.
    :type doc_xml: XmlDocument

    :return: A list of family type parameter data storage objects.
    :rtype: [:class:`.FamilyTypeParameterDataStorage`]
    """

    if isinstance(doc_xml, XmlDocument) is False:
        raise TypeError(
            "doc_xml must be an instance of XmlDocument. Got: {}".format(doc_xml)
        )

    parameters = []

    # Add an XML namespace manager
    name_space_manager = XmlNamespaceManager(doc_xml.NameTable)
    name_space_manager.AddNamespace("atom", "http://www.w3.org/2005/Atom")
    name_space_manager.AddNamespace("A", "urn:schemas-autodesk-com:partatom")

    # Get the family parameters
    for part_node in doc_xml.SelectNodes("//A:part", name_space_manager):

        # Get the family type name
        family_type_name = ""
       
        # If we got a type name, add the parameters, their values and units, parameter type and type of parameter
        if family_type_name:

            for child_node in part_node.ChildNodes:
                if child_node.Name != "title":

                    parameter = get_parameter(
                        xml_node=child_node, 
                        family_name=family_name,
                        root_category_path= root_category_path, 
                        family_path=family_path,
                        family_type_name="",
                        default_value=""
                    )
                    
                    # Add parameter to list if not in there already
                    if parameter is not None and parameter not in parameters:
                        parameters.append(parameter)

    return parameters
                   

def read_xml_into_storage(doc_xml, family_name, family_path, root_category_path = "None"):
    """
    Read the XML data into the storage object.

    Note all names and values will be encoded to ascii.

    :param doc_xml: The XML document.
    :type doc_xml: XmlDocument
    :param family_name: The name of the family.
    :type family_name: str
    :param family_path: The path of the family file.
    :type family_path: str

    :return: A family type data storage manager object.
    :rtype: :class:`.FamilyTypeDataStorageManager`
    """

    if isinstance(doc_xml, XmlDocument) is False:
        raise TypeError(
            "doc_xml must be an instance of XmlDocument. Got: {}".format(doc_xml)
        )

    type_data_storage_manager = FamilyTypeDataStorageManager()
    # Add an XML namespace manager
    name_space_manager = XmlNamespaceManager(doc_xml.NameTable)
    name_space_manager.AddNamespace("atom", "http://www.w3.org/2005/Atom")
    name_space_manager.AddNamespace("A", "urn:schemas-autodesk-com:partatom")

    # Select the family node
    family_node = doc_xml.SelectSingleNode("//A:family", name_space_manager)

    # check if category root path is not set, if so ignore use the one from the xml
    if root_category_path == "None":
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

    # it turns out that an empty parameter value means that parameter is not listed in the part atom export file for that type
    # it might be listed for another type though where it has a value...

    # need to loop over types first to ensure that all parameters are read in
    all_parameters_in_atom_export = get_unique_parameters_from_family_xml(doc_xml, family_name, root_category_path, family_path)


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

                    # get the parameter
                    parameter = get_parameter(
                        xml_node=child_node, 
                        family_name=family_name,
                        root_category_path=root_category_path, 
                        family_path=family_path,
                        family_type_name=family_type_name,
                        default_value=VALUE_UNKNOWN, # enforce parameter value to be read in
                    )

                    # Add parameter to list if valid
                    if parameter is not None:
                        # Add type to family
                        parameters.append(parameter)
            
            # check if there are parameters in the atom export that are not in the parameters list for this type since they have no value for this family type set
            

            # Set up a family type data storage object
            # make sure all values are encoded to ascii to avoid 
            # issues with special characters when writing to file
            fam_type = FamilyTypeDataStorage(
                root_name_path=encode_ascii(family_name),
                root_category_path=encode_ascii(root_category_path),
                family_name=encode_ascii(family_name),
                family_file_path=encode_ascii(family_path),
                family_type_name=encode_ascii(family_type_name),
                parameters=parameters,
                last_updated_date=last_updated_date,
                last_updated_time=last_updated_time,
            )

            # Add the family type to the storage manager for this family
            type_data_storage_manager.add_family_type_data_storage(fam_type)

    # set the family name and category if they are not set yet
    if type_data_storage_manager.family_name is None:
        type_data_storage_manager.family_name = family_name
    if type_data_storage_manager.family_category is None:
        type_data_storage_manager.family_category = root_category_path

    return type_data_storage_manager
