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


import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import (
    get_file_name_without_ext,
    get_directory_path_from_file_path,
)
from duHast.Utilities.files_xml import read_xml_file
from duHast.Revit.Family.Utility.xml_family_type_reader import read_xml_into_storage
from duHast.Revit.Family.Utility.xml_create_atom_exports import (
    write_data_to_temp_xml_file_and_read_it_back,
    write_data_to_xml_file_and_read_it_back,
)


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

    :return: A result object with .result containing a single FamilyTypeDataStorageManager object. (or empty if failed)
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


def get_family_type_data_from_library(xml_files_in_libraries, progress_callback=None):
    """
    Get the family type data from xml files in the library.
    XML where created by Revit API PartAtomExport method.

    :param xml_files_in_libraries: list of xml files to search for type data
    :type xml_files_in_libraries: [:class:`FileItem`]
    :param progress_callback: progress callback object
    :type progress_callback: :class:`ProgressBase`

    :return:
        Result class instance.

        - result.status: XML conversion status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain which xml file was read and converted into family type data.
        - result.result will be [:class:`FamilyTypeDataStorageManager`]

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = Result()
    type_data = []
    try:

        # set progress counter
        counter = 1
        max_value_xml = len(xml_files_in_libraries)

        # update progress
        if progress_callback:
            progress_callback.update(counter, max_value_xml)

        # Sort by file name to ensure consistent order when name is dispalyed in progress
        sorted_file_paths = sorted(xml_files_in_libraries, key=lambda x: os.path.basename(x.name))

        # get the type data from the library
        for xml_file in sorted_file_paths:

            # get a file name without extension to report progress
            file_name_progress = get_file_name_without_ext(xml_file.name)
            # update progress
            if progress_callback:
                progress_callback.update(counter, max_value_xml, file_name_progress)

            # read xml file
            xml_doc_status = read_xml_file(xml_file.name)
            if xml_doc_status == False:
                return_value.update_sep(
                    False,
                    "Failed to read xml file: {} with exception: {}".format(
                        xml_file.name, xml_doc_status.message
                    ),
                )
                # update progress
                counter = counter + 1
                continue
            else:
                return_value.append_message("Read xml file: {}".format(xml_file.name))

            # get the xml document
            xml_doc = xml_doc_status.result
            if xml_doc is None:
                return_value.update_sep(
                    False, "Failed to read xml file: {}".format(xml_file.name)
                )
                # update progress
                counter = counter + 1
                continue
            else:
                return_value.append_message("Retrieved xml document object")

            # build the family path (required for xml data)
            fam_name = get_file_name_without_ext(xml_file.name)
            fam_directory = get_directory_path_from_file_path(xml_file.name)
            fam_path = os.path.join(fam_directory, fam_name + ".rfa")

            # load xml data into storage
            return_value.append_message("loading family: {}".format(fam_name))
            xml_data_family = read_xml_into_storage(xml_doc, fam_name, fam_path)

            # add storage to global list
            type_data.append(xml_data_family)

            # update progress
            counter = counter + 1

            # check for user cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )

    # store data to be returned
    return_value.result = type_data

    return return_value
