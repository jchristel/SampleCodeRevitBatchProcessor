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

from csv import QUOTE_MINIMAL


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.family_types import (
    get_all_family_type_names, 
    delete_family_type, 
    create_family_type, 
    DEFAULT_CATALOGUE_REFERENCE_FAMILY_TYPE,
)
from duHast.Revit.Family.family_parameter_utils import set_family_parameter_value

from duHast.Utilities.files_io import file_exist
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv
from duHast.Utilities.Objects.file_encoding_bom import BOMValue


# if a default family type is created, these parameters will be reset to their default values
PARAMETERS_TO_RESET = [
    "HSL_AHFG_CODE",
    "HSL_AHFG_DESCRIPTION",
    "HSL_BUDGET_GROUP",
    "Description",
    "HSL_ID_TYPE",
    "Uniclass2015Code",
    "Uniclass2015Title",
    "Uniclass2015Version",
]

def update_type_catalogue_file(doc,  maintain_types_list):
    """
    Updates the type catalogue file for a family document by removing types that are not in the maintain list.

    :param doc: The family document to process.
    :type doc: :class:`Autodesk.Revit.DB.Document`
    :param maintain_types_list: A list of types to maintain, where each entry is a tuple (family_name, type_name).
    :type maintain_types_list: list of nested lists, each containing two strings: [family_name, type_name]
    :return: Result object containing the status and messages.
    :rtype: :class:`duHast.Utilities.Objects.result.Result`
    """

    return_value = Result()
    try:
        return_value.append_message(
            "Checking for type catalogue file for family '{}'...".format(doc.PathName)
        )

        # check if catalogue file exists
        catalogue_file_name =doc.PathName
        catalogue_file_name = catalogue_file_name[:-4] + ".txt"

        if not file_exist(catalogue_file_name):
            return_value.update_sep(
                True,
                "No type catalogue file found for family '{}'.".format(doc.Title),
            )
            return return_value
        
        return_value.append_message(
            "Found type catalogue file for family: {}".format(catalogue_file_name)
        )
        
        # read the type catalogue file
        read_result = read_csv_file(catalogue_file_name)

        if not read_result.status:
            return_value.update_sep(
                False,
                "Failed to read type catalogue file for family '{}': {}".format(doc.Title, read_result.message),
            )
            return return_value
        
        # the type name is the first entry in every data row, ignore the header row
        type_catalogue_data = read_result.result[1:]  # skip header row
        header_row = read_result.result[:1][0]  # keep the header row
        type_rows_to_maintain = []

        for row in type_catalogue_data:
            # check if the family name matches
            if row[0] in maintain_types_list:
                type_rows_to_maintain.append(row)

         # remove BOM from header row if it exists
        header_row[0] = "" 

        # write data back to file
        write_result = write_report_data_as_csv(
            file_name= catalogue_file_name,
            encoding="utf-16-le",
            bom=BOMValue.UTF_16_LITTLE_ENDIAN,
            header = header_row, # keep the header row from the read result
            data = type_rows_to_maintain,
            quoting= QUOTE_MINIMAL,  # use minimal quoting for CSV
        )
    
        return_value.update(write_result)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to update type catalogue file in family '{}': {}".format(doc.Title, e),
        )
    return return_value


def get_names_of_types_to_keep(family_name, maintain_types_list):

    types_to_keep = []
    search_name = "{}.rfa".format(family_name)

    # loop over maintain types list and find the family name
    for family_type_row in maintain_types_list:
        if family_type_row[0] == search_name:
            types_to_keep.append(family_type_row[1])

    return types_to_keep


def create_default_type(doc, types_to_delete):
    """
    Creates a default family type in the family document if a catalogue file is in use...

    :param doc: The family document to process.
    :type doc: :class:`Autodesk.Revit.DB.Document`
    :return: Result object containing the status and messages.
    :rtype: :class:`duHast.Utilities.Objects.result.Result`
    """
    
    return_value = Result()
    try:

        # check if the default family type already exists
        if DEFAULT_CATALOGUE_REFERENCE_FAMILY_TYPE in types_to_delete:
            return_value.update_sep(
                True,
                "Default type '{}' already exists in family '{}'.".format(
                    DEFAULT_CATALOGUE_REFERENCE_FAMILY_TYPE, doc.Title
                ),
            )
            return return_value

        # create default catalogue type
        create_type_result = create_family_type(doc, DEFAULT_CATALOGUE_REFERENCE_FAMILY_TYPE)

        if not create_type_result.status:
            return_value.update_sep(
                False,
                "Failed to create default type in family '{}': {}".format(doc.Title, create_type_result.message),
            )
            return return_value
        
        # Get the FamilyManager
        family_manager = doc.FamilyManager

        # reset parameters
        for para_name in PARAMETERS_TO_RESET:
            # Get the parameter
            parameter = family_manager.get_Parameter(para_name)
            if parameter:
                set_result = set_family_parameter_value(doc, family_manager, parameter, DEFAULT_CATALOGUE_REFERENCE_FAMILY_TYPE)
                return_value.update(set_result)
            else: 
                return_value.append_message("Parameter not found: {}".format(para_name))

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to create default type in family '{}': {}".format(doc.Title, e),
        )
        return return_value
    return return_value


def delete_non_conforming_types(doc, maintain_types_list):
    """
    Delete non-conforming types in a family document based on a list of types to maintain.

    Note
    
    Types reported might only live in a type catalogue file. In that case the family may only contain a place holder type with name "Refer To Catalog File" or similar.

    :param doc: The family document to process.
    :type doc: :class:`Autodesk.Revit.DB.Document`
    :param maintain_types_list: A list of types to maintain, where each entry is a tuple (family_name, type_name).
    :type maintain_types_list: list of nested lists, each containing two strings: [family_name, type_name]

    :return: Result object containing the status and messages.
    :rtype: :class:`duHast.Utilities.Objects.result.Result`
    """
    return_value = Result()

    try:
        # get the family name
        family_name = doc.Title

        # build list of types to keep
        types_to_keep = get_names_of_types_to_keep(family_name, maintain_types_list)
        return_value.append_message(
            "Types to keep in family '{}': {}".format(family_name, len(types_to_keep))
        )

        all_type_names_result = get_all_family_type_names(doc)
        
        # check if we got any current type names
        if (not all_type_names_result.status):
            return_value.update_sep(
                False,
                "Failed to get all family type names: {}".format(all_type_names_result.message),
            )
            return return_value
        
        return_value.append_message(
            "Found {} types in family '{}'.".format(len(all_type_names_result.result), family_name)
        )
        
        # get all type names in family
        all_type_names = all_type_names_result.result

        # get list of names to delete
        types_to_delete = [name for name in all_type_names if name not in types_to_keep]

        if len(types_to_delete) == 0:
            return_value.update_sep(
                True,
                "No types to delete in family '{}'.".format(family_name),
            )
            return return_value
        
        # check if we are deleting all types in a family... if that is the case we will need to create a default type first
        if len(types_to_delete) == len(all_type_names):
            print("Deleting all types in family '{}'. Creating default type first.".format(family_name))
            create_default_result = create_default_type(doc, types_to_delete)
            if not create_default_result.status:
                return_value.update_sep(
                    False,
                    "Failed to create default type in family '{}': {}".format(family_name, create_default_result.message),
                )
                return return_value
            return_value.append_message(
                "Created default type in family '{}' successfully.".format(family_name)
            )

        # delete all other types
        for type_name in types_to_delete:
            # check if this is the default type
            if type_name == DEFAULT_CATALOGUE_REFERENCE_FAMILY_TYPE:
                return_value.append_message(
                    "Skipping deletion of default type '{}' in family '{}'.".format(type_name, family_name)
                )
                continue
            print("Deleting type '{}' in family '{}'...".format(type_name, family_name))
            delete_result = delete_family_type(doc, type_name)
            if not delete_result.status:
                return_value.append_message(
                    "Failed to delete type '{}': {}".format(type_name, delete_result.message)
                )
            else:
                return_value.append_message(
                    "Deleted type '{}' successfully.".format(type_name)
                )
        
        # fix up any type catalogue file
        update_type_catalogue_file_result = update_type_catalogue_file(doc, types_to_keep)
        return_value.update( update_type_catalogue_file_result)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to delete non confirming types: {}".format(e),
        )
    
    return return_value