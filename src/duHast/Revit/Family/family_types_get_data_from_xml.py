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


import tempfile
import os

from Autodesk.Revit.DB import Element

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import (
    get_file_name_without_ext,
    get_directory_path_from_file_path,
)
from duHast.Utilities.files_xml import read_xml_file
from duHast.Revit.Family.Utility.xml_family_type_reader import read_xml_into_storage
from duHast.Revit.Family.family_functions import get_symbol_names_of_family


def write_data_to_xml_file(application, family_path, xml_path):
    """
    Write the family type data to an XML file.

    :param application: The Revit application object.
    :type application: Autodesk.Revit.ApplicationServices.Application
    :param family_path: The path of the family file.
    :type family_path: str
    :param xml_path: The path of the XML file.
    :type xml_path: str

    :return: A result object with .status True if successful.
    :rtype: Result
    """

    return_value = Result()
    try:

        # Save XML file to temporary location
        # this is a method of the application object and does not require the family to be open...
        application.ExtractPartAtomFromFamilyFile(family_path, xml_path)
        return_value.update_sep(True, "Wrote data to XML file.")
    except Exception as e:
        return_value.update_sep(False, "Failed to write XML data: {}".format(e))

    return return_value


def write_data_to_temp_xml_file_and_read_it_back(an_action_to_write_xml_data):
    """
    Write the data to a temp XML file and read it back.

    :param an_action_to_write_xml_data: The action to write the XML data.
    :type an_action_to_write_xml_data: function returning a Result object

    :return:
        Result class instance.

        - result.status: True if data was written and read back successfully, False otherwise.
        - result.message will contain the log data.
        - result.result will be a XML document object.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = Result()

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
        temp_path_xml = temp_file.name

    try:

        # Write the data to the file
        write_result = an_action_to_write_xml_data(temp_path_xml)
        # update the return value
        return_value.update(write_result)

        # Check if the write was successful
        if return_value.status is False:
            return return_value

        # Read the data back from the file
        read_result = read_xml_file(temp_path_xml)

        # update the return value message and status
        # for some reasons this adds a XMLDeclaration object to the result field...not sure why
        return_value.update(read_result)

        # overwrite result field with the actual XML document
        return_value.result = read_result.result

    finally:
        # Delete the temporary file
        if os.path.exists(temp_path_xml):
            os.remove(temp_path_xml)

    return return_value


def write_data_to_xml_file_and_read_it_back(an_action_to_write_xml_data, xml_file_path):
    """
    Write the data to an XML file and read it back.

    :param an_action_to_write_xml_data: The action to write the XML data.
    :type an_action_to_write_xml_data: function
    :param xml_file_path: The path of the XML file.
    :type xml_file_path: str

    :return:
        Result class instance.

        - result.status: True if data was written and read back successfully, False otherwise.
        - result.message will contain log data
        - result.result will be a XML document object.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:

        # Write the data to the file
        write_result = an_action_to_write_xml_data(xml_file_path)

        # update the return value
        return_value.update(write_result)

        # Check if the write was successful
        if return_value.status is False:
            return return_value

        # Read the data back from the file
        read_result = read_xml_file(xml_file_path)

        # update the return value message and status
        # for some reasons this adds a XMLDeclaration object to the result field...not sure why
        return_value.update(read_result)
        # overwrite result field with the actual XML document
        return_value.result = read_result.result

    except Exception as e:
        return_value.update_sep(False, "{}".format(e))
    return return_value


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
    try:
        # set up action to write xml data
        def action(temp_path_xml):
            action_return_value = Result()
            try:
                # Save XML file to temporary location
                # this is a method of the application object and does not require the family to be open...
                application.ExtractPartAtomFromFamilyFile(family_path, temp_path_xml)
                action_return_value.update_sep(True, "Wrote data to XML file.")
            except Exception as e:
                action_return_value.update_sep(
                    False, "Failed to write XML data: {}".format(e)
                )
            return action_return_value

        doc_xml_result = Result()

        if use_temporary_file:
            # Write the data to an XML file and read it back
            doc_xml_result = write_data_to_temp_xml_file_and_read_it_back(action)
        else:
            dir_out = get_directory_path_from_file_path(family_path)
            family_name = get_file_name_without_ext(family_path)
            return_value.append_message(
                "Writing XML data to file: {}".format(
                    os.path.join(dir_out, family_name + ".xml")
                )
            )
            # Write the data to an XML file and read it back
            doc_xml_result = write_data_to_xml_file_and_read_it_back(
                action, os.path.join(dir_out, family_name + ".xml")
            )

        return_value.update(doc_xml_result)

        # check if an xml document was created
        if doc_xml_result.status is False:
            return return_value

        # read the xml data into the storage object
        type_data = read_xml_into_storage(
            doc_xml_result.result, family_name, family_path
        )

        # store list in return object ( clear any previous results )
        return_value.result = [type_data]
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
    try:
        # set up action to write xml data
        def action(temp_path_xml):
            action_return_value = Result()
            try:
                # Save XML file to temporary location
                revit_family.ExtractPartAtom(temp_path_xml)
                action_return_value.update_sep(True, "Wrote data to XML file")
            except Exception as e:
                action_return_value.update_sep(
                    False, "Failed to write XML data: {}".format(e)
                )
            return action_return_value

        # Write the data to an XML file and read it back
        doc_xml_result = write_data_to_temp_xml_file_and_read_it_back(action)
        return_value.update(doc_xml_result)

        # check if an xml document was created
        if doc_xml_result.status is False:
            return return_value

        # read the xml data into the storage object
        type_data = read_xml_into_storage(
            doc_xml_result.result,
            family_name=Element.Name.GetValue(revit_family),
            family_path="",
        )

        # it looks like the part atom extraction does sometime include types which are no longer present
        # in the family document (ghost types) so we need to check if we have any types
        # since family inherits from Element, I should be able to get the document from the family object
        # and check if the types are still present in the document
        symbol_names = get_symbol_names_of_family(revit_family)
        type_data.remove_ghost_types(symbol_names)
    
        # store list in return object ( clear any previous results )
        return_value.result = [type_data]
    except Exception as e:
        return_value.update_sep(False, "{}".format(e))

    return return_value
